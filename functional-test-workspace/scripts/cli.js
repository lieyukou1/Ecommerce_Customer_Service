#!/usr/bin/env node
import path from "node:path";
import { createResolvedConfig } from "./config.js";
import { timestampForFolder, ensureDir, writeJson, writeText, printSection } from "./utils.js";
import { BreakpointController } from "./breakpoint.js";
import { runPrecheck } from "./precheck.js";
import { runApiScenarios } from "./api-runner.js";
import { runBrowserScenarios } from "./browser-runner.js";
import { buildMarkdownReport, buildRegressionBaselineMarkdown } from "./reporter.js";
import { apiScenarios } from "../scenarios/api-scenarios.js";
import { browserScenarios } from "../scenarios/browser-scenarios.js";

async function main() {
  const [, , command, ...args] = process.argv;
  const breakpointEnabled = args.includes("--breakpoint");
  const config = createResolvedConfig();

  if (!command || !["precheck", "run"].includes(command)) {
    process.stderr.write("Usage: node ./scripts/cli.js <precheck|run> [--breakpoint]\n");
    return 1;
  }

  const precheck = await runPrecheck(config);
  printSection("Precheck", precheck);

  if (command === "precheck") {
    return precheck.ok ? 0 : 1;
  }

  const runAt = new Date().toISOString();
  const artifactsDir = path.join(process.cwd(), "reports", timestampForFolder(new Date()));
  await ensureDir(artifactsDir);

  const breakpointController = new BreakpointController(breakpointEnabled);
  await breakpointController.pause("precheck", precheck);

  const api = await runApiScenarios({
    config,
    scenarios: apiScenarios,
    breakpointController,
  });

  const browser = config.skipBrowserSmoke
    ? []
    : await runBrowserScenarios({
        config,
        scenarios: browserScenarios,
        breakpointController,
        artifactsDir,
      });

  const runSummary = {
    api,
    browser,
  };

  await breakpointController.pause("run-summary", runSummary);
  await breakpointController.close();

  const reportJson = {
    runAt,
    config,
    precheck,
    runSummary,
  };
  const reportMarkdown = buildMarkdownReport({
    runAt,
    config,
    precheck,
    runSummary,
  });
  const regressionBaselineMarkdown = buildRegressionBaselineMarkdown({
    runAt,
    scenarios: apiScenarios,
  });

  await writeJson(path.join(artifactsDir, "run.json"), reportJson);
  await writeText(path.join(artifactsDir, "report.md"), reportMarkdown);
  await writeText(path.join(artifactsDir, "regression-baseline.md"), regressionBaselineMarkdown);

  printSection("Artifacts", {
    artifactsDir,
    files: [
      path.join(artifactsDir, "run.json"),
      path.join(artifactsDir, "report.md"),
      path.join(artifactsDir, "regression-baseline.md"),
    ],
  });

  return 0;
}

main()
  .then((exitCode) => {
    if (typeof exitCode === "number") {
      process.exitCode = exitCode;
    }
  })
  .catch((error) => {
    process.stderr.write(`${error instanceof Error ? error.stack || error.message : String(error)}\n`);
    process.exitCode = 1;
  });
