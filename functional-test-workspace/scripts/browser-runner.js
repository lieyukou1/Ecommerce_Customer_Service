import path from "node:path";
import fs from "node:fs";
import { pathToFileURL } from "node:url";
import { classifyScenarioResult } from "./utils.js";

const PLAYWRIGHT_CANDIDATE_PATHS = [
  "C:\\Users\\LiuYang\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\.pnpm\\playwright@1.60.0\\node_modules\\playwright\\index.js",
  "C:\\Users\\LiuYang\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\playwright\\index.js",
];

async function loadPlaywright(modulePath) {
  const tried = [];
  for (const candidate of [modulePath, ...PLAYWRIGHT_CANDIDATE_PATHS]) {
    if (!candidate || tried.includes(candidate) || !fs.existsSync(candidate)) {
      continue;
    }
    tried.push(candidate);
    try {
      return await import(pathToFileURL(candidate).href);
    } catch (error) {
      if (candidate === PLAYWRIGHT_CANDIDATE_PATHS.at(-1)) {
        throw error;
      }
    }
  }
  throw new Error("未找到可用的 Playwright 模块路径");
}

function buildInterceptState() {
  return {
    apiCalls: [],
    historyCalls: [],
    commerceCalls: [],
  };
}

function safeParseJson(text) {
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    return {
      _raw: text,
    };
  }
}

async function installRoutes(page, config, interceptState) {
  await page.route("**/api/chat/history**", async (route) => {
    const request = route.request();
    const requestUrl = new URL(request.url());
    interceptState.historyCalls.push({
      url: request.url(),
      method: request.method(),
    });

    try {
      const response = await fetch(
        `${config.localAssistantBaseUrl}/api/chat/history?resident_id=${encodeURIComponent(
          requestUrl.searchParams.get("resident_id") || config.defaultResidentId,
        )}`,
      );
      const responseBody = await response.text();
      await route.fulfill({
        status: response.status,
        contentType: "application/json",
        body: responseBody,
      });
    } catch (error) {
      await route.fulfill({
        status: 502,
        contentType: "application/json",
        body: JSON.stringify({
          detail: error instanceof Error ? error.message : String(error),
        }),
      });
    }
  });

  await page.route("**/api/chat", async (route) => {
    const request = route.request();
    const originalBody = request.postDataJSON() || {};
    const forwardedBody = {
      ...originalBody,
      resident_id: originalBody.resident_id || originalBody.sender_id || config.defaultResidentId,
    };
    delete forwardedBody.sender_id;

    let status = null;
    let responseBody = null;
    let error = null;

    try {
      const response = await fetch(`${config.localAssistantBaseUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(forwardedBody),
      });
      status = response.status;
      responseBody = await response.text();
      await route.fulfill({
        status,
        contentType: "application/json",
        body: responseBody,
      });
    } catch (caught) {
      error = caught instanceof Error ? caught.message : String(caught);
      await route.fulfill({
        status: 502,
        contentType: "application/json",
        body: JSON.stringify({
          detail: error,
        }),
      });
    }

    interceptState.apiCalls.push({
      url: request.url(),
      method: request.method(),
      originalBody,
      forwardedBody,
      status,
      responseBody,
      error,
    });
  });

  await page.route("**/commerce/**", async (route) => {
    const request = route.request();
    interceptState.commerceCalls.push({
      url: request.url(),
      method: request.method(),
    });
    await route.continue();
  });
}

async function buildPageSnapshot(page) {
  return page.evaluate(() => {
    const bubbles = Array.from(document.querySelectorAll(".bot-bubble p"))
      .slice(-3)
      .map((node) => node.textContent?.trim() || "");
    const userBubbles = Array.from(document.querySelectorAll(".user-bubble p"))
      .slice(-2)
      .map((node) => node.textContent?.trim() || "");
    const sidebarCards = document.querySelectorAll(".sidebar-card").length;
    return {
      recentBotTexts: bubbles,
      recentUserTexts: userBubbles,
      sidebarCardCount: sidebarCards,
    };
  });
}

async function setResidentId(page, residentId) {
  await page.locator(".controls input[type='text']").fill(residentId);
}

async function executeBrowserStep(page, step) {
  if (step.kind === "loadSidebar") {
    await page.locator(".controls .secondary-button").click();
    return;
  }

  if (step.kind === "clickWorkOrderCard") {
    await page.locator(".sidebar-card button").first().click();
    return;
  }

  if (step.kind === "switchToServiceItems") {
    await page.locator(".tabs .tab-button").nth(1).click();
    return;
  }

  if (step.kind === "clickServiceItemCard") {
    await page.locator(".sidebar-card button").first().click();
    return;
  }

  if (step.kind === "sendText") {
    await page.locator(".composer input").fill(step.text);
    await page.locator(".composer button[type='submit']").click();
  }
}

export async function runBrowserScenarios({
  config,
  scenarios,
  breakpointController,
  artifactsDir,
}) {
  const playwrightModule = await loadPlaywright(config.browserModulePath);
  const chromium = playwrightModule.chromium || playwrightModule.default?.chromium;
  if (!chromium) {
    throw new Error("Playwright 模块已加载，但未找到 chromium 导出");
  }
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const interceptState = buildInterceptState();
  const scenarioLogs = [];
  const pageErrors = [];

  page.on("pageerror", (error) => {
    pageErrors.push(error.message);
  });

  await installRoutes(page, config, interceptState);

  for (const scenario of scenarios) {
    await page.goto(config.frontendBaseUrl, { waitUntil: "networkidle" });
    await setResidentId(page, scenario.residentId);
    const stepLogs = [];

    for (const step of scenario.steps) {
      const apiCallCountBefore = interceptState.apiCalls.length;
      const pageErrorCountBefore = pageErrors.length;

      await executeBrowserStep(page, step);
      await page.waitForTimeout(700);

      const pageSnapshot = await buildPageSnapshot(page);
      const lastApiCall =
        interceptState.apiCalls.length > apiCallCountBefore
          ? interceptState.apiCalls[interceptState.apiCalls.length - 1]
          : null;

      const parsedResponse = safeParseJson(lastApiCall?.responseBody);
      const latestPageError =
        pageErrors.length > pageErrorCountBefore ? pageErrors[pageErrors.length - 1] : null;

      const verdict = classifyScenarioResult({
        statusCode: lastApiCall?.status || (step.kind === "loadSidebar" ? 200 : null),
        error:
          latestPageError ||
          lastApiCall?.error ||
          (step.kind === "loadSidebar" && pageSnapshot.sidebarCardCount === 0
            ? "侧栏未加载出任何对象卡片"
            : null),
        messages:
          parsedResponse && Array.isArray(parsedResponse.messages)
            ? parsedResponse.messages
            : step.kind === "loadSidebar"
              ? [{}]
              : [],
      });

      const screenshotPath = path.join(artifactsDir, `${scenario.id}_${step.id}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });

      const stepLog = {
        scenario_id: scenario.id,
        step_id: step.id,
        channel: "browser",
        request: lastApiCall
          ? {
              target: `${config.localAssistantBaseUrl}/api/chat`,
              body: lastApiCall.forwardedBody,
              browser_original_body: lastApiCall.originalBody,
            }
          : {
              target: step.kind,
              body: null,
            },
        response: lastApiCall
          ? {
              status: lastApiCall.status,
              body: parsedResponse,
              error: lastApiCall.error,
            }
          : {
              status: 200,
              body: null,
              error: latestPageError,
            },
        page_snapshot: {
          ...pageSnapshot,
          screenshot: screenshotPath,
        },
        result: verdict.result,
        reason: verdict.reason,
      };

      stepLogs.push(stepLog);

      if (
        step.kind === "sendText" ||
        step.kind === "clickWorkOrderCard" ||
        step.kind === "clickServiceItemCard"
      ) {
        await breakpointController.pause(`${scenario.id}/${step.id}`, stepLog);
      }
    }

    const scenarioResult = stepLogs.some((log) => log.result === "infra_fail")
      ? "infra_fail"
      : stepLogs.some((log) => log.result === "behavior_fail")
        ? "behavior_fail"
        : stepLogs.some((log) => log.result === "placeholder_pass")
          ? "placeholder_pass"
          : "pass";

    scenarioLogs.push({
      scenario,
      result: scenarioResult,
      steps: stepLogs,
    });
  }

  await browser.close();
  return scenarioLogs;
}
