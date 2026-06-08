import fs from "node:fs/promises";
import path from "node:path";

export const PLACEHOLDER_HINTS = [
  "还没做到",
  "暂未实现",
  "占位",
];

export function timestampForFolder(date = new Date()) {
  const pad = (value) => String(value).padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    "_",
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join("");
}

export async function ensureDir(dirPath) {
  await fs.mkdir(dirPath, { recursive: true });
}

export async function writeJson(filePath, data) {
  await ensureDir(path.dirname(filePath));
  await fs.writeFile(filePath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

export async function writeText(filePath, text) {
  await ensureDir(path.dirname(filePath));
  await fs.writeFile(filePath, text, "utf8");
}

export function extractBotTexts(messages = []) {
  return messages
    .map((message) => message?.text || "")
    .filter(Boolean);
}

export function summarizeMessages(messages = []) {
  return messages.map((message, index) => {
    if (message.object) {
      return {
        index,
        type: "object",
        objectType: message.object.type,
        objectId: message.object.id,
        title: message.object.title || "",
      };
    }

    return {
      index,
      type: "text",
      text: message.text || "",
    };
  });
}

export function detectPlaceholder(messages = []) {
  const joinedText = extractBotTexts(messages).join("\n");
  return PLACEHOLDER_HINTS.some((hint) => joinedText.includes(hint));
}

export function classifyScenarioResult({
  statusCode,
  error,
  messages,
  assertionErrors = [],
}) {
  if (error) {
    return {
      result: "infra_fail",
      reason: error,
    };
  }

  if (!statusCode) {
    return {
      result: "infra_fail",
      reason: "Request did not return a usable HTTP status",
    };
  }

  if (statusCode >= 500) {
    return {
      result: "infra_fail",
      reason: `HTTP ${statusCode}`,
    };
  }

  if (!Array.isArray(messages) || messages.length === 0) {
    return {
      result: "infra_fail",
      reason: "Response did not contain bot messages",
    };
  }

  if (assertionErrors.length > 0) {
    return {
      result: "behavior_fail",
      reason: assertionErrors.join("; "),
    };
  }

  if (detectPlaceholder(messages)) {
    return {
      result: "placeholder_pass",
      reason: "Main chain is alive, but the response still hit a known placeholder path",
    };
  }

  return {
    result: "pass",
    reason: "Response and state assertions matched expectations",
  };
}

export function countByResult(entries = []) {
  const counts = {
    pass: 0,
    placeholder_pass: 0,
    behavior_fail: 0,
    infra_fail: 0,
  };

  for (const entry of entries) {
    if (entry?.result && counts[entry.result] !== undefined) {
      counts[entry.result] += 1;
    }
  }

  return counts;
}

export function printSection(title, payload) {
  process.stdout.write(`\n=== ${title} ===\n`);
  if (typeof payload === "string") {
    process.stdout.write(`${payload}\n`);
    return;
  }
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
}
