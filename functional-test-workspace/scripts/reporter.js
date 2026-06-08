import { countByResult } from "./utils.js";

function renderCheck(check) {
  const statusText = check.skipped ? "SKIP" : check.ok ? "PASS" : "FAIL";
  const detail = check.error
    ? check.error
    : typeof check.body === "string"
      ? check.body.slice(0, 160)
      : JSON.stringify(check.body).slice(0, 160);

  return `- [${statusText}] ${check.title} \`${check.target}\`\n  - status: ${check.status ?? "unreachable"}\n  - detail: ${detail}`;
}

function renderResultSummary(entries) {
  const counts = countByResult(entries);
  return [
    `- pass: ${counts.pass}`,
    `- placeholder_pass: ${counts.placeholder_pass}`,
    `- behavior_fail: ${counts.behavior_fail}`,
    `- infra_fail: ${counts.infra_fail}`,
  ].join("\n");
}

function renderApiScenario(entry) {
  const lines = [
    `### ${entry.scenario.id} - ${entry.scenario.title}`,
    `- result: \`${entry.result}\``,
    `- tags: ${(entry.scenario.tags || []).map((tag) => `\`${tag}\``).join(", ") || "(none)"}`,
    `- source: \`${entry.scenario.source || "unspecified"}\``,
  ];

  for (const turn of entry.turns || []) {
    lines.push(`- turn \`${turn.step_id}\`: \`${turn.result}\` - ${turn.reason}`);
    lines.push(`  - inferred track: \`${turn.track}\``);
    if (turn.assertion_errors?.length) {
      lines.push(`  - assertion errors: ${turn.assertion_errors.join(" | ")}`);
    }
    if (turn.request?.body) {
      lines.push(`  - request: \`${JSON.stringify(turn.request.body)}\``);
    }
    if (turn.state_snapshot) {
      lines.push(`  - state: \`${JSON.stringify(turn.state_snapshot)}\``);
    }
  }

  if (entry.final_assertions?.length) {
    lines.push(`- final assertion errors: ${entry.final_assertions.join(" | ")}`);
  }

  if (entry.final_state_snapshot) {
    lines.push(`- final state: \`${JSON.stringify(entry.final_state_snapshot)}\``);
  }

  return lines.join("\n");
}

function renderBrowserScenario(entry) {
  const lines = [
    `### ${entry.scenario.id} - ${entry.scenario.title}`,
    `- result: \`${entry.result}\``,
  ];

  for (const step of entry.steps || []) {
    lines.push(`- step \`${step.step_id}\`: \`${step.result}\` - ${step.reason}`);
    if (step.page_snapshot?.recentBotTexts?.length) {
      lines.push(`  - recent bot texts: ${step.page_snapshot.recentBotTexts.join(" | ")}`);
    }
    if (step.page_snapshot?.screenshot) {
      lines.push(`  - screenshot: \`${step.page_snapshot.screenshot}\``);
    }
  }

  return lines.join("\n");
}

function renderKnownGaps() {
  return [
    "- Browser smoke still focuses on page wiring and basic request forwarding. Deep state assertions remain on the API regression side.",
    "- Track classification is currently inferred from state plus reply text, not emitted explicitly by the runtime.",
    "- Long-dialogue regression currently resets state through the new test-only state snapshot API before each scenario.",
  ].join("\n");
}

function renderRecommendations(runSummary) {
  const hasBrowserFailure = runSummary.browser.some((scenario) => scenario.result === "infra_fail" || scenario.result === "behavior_fail");
  const hasApiFailure = runSummary.api.some((scenario) => scenario.result === "infra_fail" || scenario.result === "behavior_fail");
  const hasPlaceholder = runSummary.api.some((scenario) => scenario.result === "placeholder_pass");

  const suggestions = [];
  if (hasApiFailure) {
    suggestions.push("- Investigate the failing API regression turns first. The state snapshots now tell you exactly when context drift begins.");
  }
  if (hasPlaceholder) {
    suggestions.push("- Placeholder passes mean the main chain is alive but some business branch is still unfinished or too mechanical.");
  }
  if (hasBrowserFailure) {
    suggestions.push("- Fix browser smoke failures after API regressions are stable, so frontend wiring is checked against a healthier backend baseline.");
  }
  if (!hasApiFailure && !hasBrowserFailure && !hasPlaceholder) {
    suggestions.push("- This run is good enough to serve as the current optimization-phase baseline. Keep it as the reference before the next stage change.");
  }
  suggestions.push("- After each optimization batch, re-run precheck, long-dialogue regression, and browser smoke together so behavior drift is visible immediately.");
  return suggestions.join("\n");
}

export function buildRegressionBaselineMarkdown({ runAt, scenarios }) {
  const groups = new Map();

  for (const scenario of scenarios) {
    const primaryTag = scenario.tags?.[0] || "ungrouped";
    if (!groups.has(primaryTag)) {
      groups.set(primaryTag, []);
    }
    groups.get(primaryTag).push(scenario);
  }

  const lines = [
    "# Long Dialogue Regression Baseline",
    "",
    `- generated_at: \`${runAt}\``,
    `- scenario_count: \`${scenarios.length}\``,
    "",
    "## Coverage Rules",
    "- Every scenario is a multi-turn chain instead of a 1-2 turn smoke check.",
    "- Each turn asserts state fields and message semantics together.",
    "- Each scenario starts from a reset state, with optional future support for seeded state snapshots.",
    "",
    "## Scenario Groups",
  ];

  for (const [group, groupScenarios] of groups.entries()) {
    lines.push("");
    lines.push(`### ${group}`);
    for (const scenario of groupScenarios) {
      lines.push(`- \`${scenario.id}\` (${scenario.turns.length} turns)`);
      lines.push(`  - tags: ${(scenario.tags || []).join(", ")}`);
      lines.push(`  - source: ${scenario.source || "unspecified"}`);
      lines.push(`  - title: ${scenario.title}`);
    }
  }

  return `${lines.join("\n")}\n`;
}

export function buildMarkdownReport({ runAt, config, precheck, runSummary }) {
  const lines = [
    "# Functional Test Run Report",
    "",
    `- run_at: \`${runAt}\``,
    `- frontend: \`${config.frontendBaseUrl}\``,
    `- local_assistant: \`${config.localAssistantBaseUrl}\``,
    `- property_backend: \`${config.propertyBackendBaseUrl}\``,
    `- default_resident_id: \`${config.defaultResidentId}\``,
    "",
    "## Precheck",
    ...precheck.checks.map(renderCheck),
    "",
    "## API Long Dialogue Regression Summary",
    renderResultSummary(runSummary.api),
    "",
    "## API Long Dialogue Regression Details",
    ...runSummary.api.map(renderApiScenario),
    "",
    "## Browser Smoke Summary",
    renderResultSummary(runSummary.browser),
    "",
    "## Browser Smoke Details",
    ...runSummary.browser.map(renderBrowserScenario),
    "",
    "## Known Gaps",
    renderKnownGaps(),
    "",
    "## Next Focus",
    renderRecommendations(runSummary),
    "",
  ];

  return `${lines.join("\n")}\n`;
}
