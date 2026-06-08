export const DEFAULT_CONFIG = {
  frontendBaseUrl: process.env.FRONTEND_BASE_URL || "http://127.0.0.1:5173",
  localAssistantBaseUrl: process.env.LOCAL_ASSISTANT_BASE_URL || "http://127.0.0.1:18082",
  propertyBackendBaseUrl: process.env.PROPERTY_BACKEND_BASE_URL || "http://192.168.200.145:18081",
  defaultResidentId: process.env.DEFAULT_TEST_RESIDENT_ID || "r1001",
  skipPropertyBackendPrecheck: process.env.SKIP_PROPERTY_BACKEND_PRECHECK === "1",
  skipBrowserSmoke: process.env.SKIP_BROWSER_SMOKE === "1",
  browserModulePath:
    process.env.PLAYWRIGHT_MODULE_PATH ||
    "C:\\Users\\LiuYang\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules\\.pnpm\\playwright@1.60.0\\node_modules\\playwright\\index.js",
};

export function createResolvedConfig(overrides = {}) {
  return {
    ...DEFAULT_CONFIG,
    ...overrides,
  };
}
