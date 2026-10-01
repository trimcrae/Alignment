// Produced by OpenAI Codex (AI agent), usage-sprint-2026-10-01. Human review not performed.
// Read-only CLI; Node built-ins only, no network requests, environment secrets or data writes.
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { validateLedger, summarizeLedger } from "./ledger-core.mjs";
import { runLedgerTests } from "./ledger-tests.mjs";

async function main() {
  const args = process.argv.slice(2);
  if (args.length !== 1 || !["validate","test","summary"].includes(args[0])) {
    console.error("Usage: node projects/model-safety-ledger/ledger-tool.mjs validate|test|summary");
    process.exitCode = 2; return;
  }
  const [ledgerText, receiptText] = await Promise.all([
    readFile(new URL("./ledger.json", import.meta.url), "utf8"),
    readFile(new URL("./evidence/primary-acquisition.json", import.meta.url), "utf8"),
  ]);
  const ledger = JSON.parse(ledgerText), receipt = JSON.parse(receiptText);
  const hash = createHash("sha256").update(receiptText, "utf8").digest("hex");
  const result = validateLedger(ledger, receipt, hash);
  if (!result.valid) { console.error(JSON.stringify(result, null, 2)); process.exitCode = 1; return; }
  console.log(JSON.stringify(args[0] === "test" ? runLedgerTests(ledger, receiptText) :
    args[0] === "summary" ? summarizeLedger(ledger) : result, null, 2));
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });
