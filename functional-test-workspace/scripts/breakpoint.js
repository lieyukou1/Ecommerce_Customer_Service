import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import { printSection } from "./utils.js";

export class BreakpointController {
  constructor(enabled) {
    this.enabled = enabled;
    this.rl = enabled ? readline.createInterface({ input, output }) : null;
  }

  async pause(title, payload) {
    if (!this.enabled) {
      return;
    }

    printSection(`断点: ${title}`, payload);
    await this.rl.question("按 Enter 继续...");
  }

  async close() {
    await this.rl?.close();
  }
}
