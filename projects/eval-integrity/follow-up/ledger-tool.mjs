#!/usr/bin/env node
// Produced by OpenAI Codex (AI agent), usage-sprint-2026-10-01.
// Node 20+; no dependencies. GET requests only, no artifact writes.
import { readFile } from "node:fs/promises";
import { validateLedger, summarizeRecord, checkUpstream } from "./ledger-core.mjs";
import { runLedgerTests } from "./ledger-tests.mjs";

async function main() {
  const [command = "validate", path, ...extra] = process.argv.slice(2);
  if (!["validate", "test", "check"].includes(command) || extra.length) {
    throw new Error("Usage: node ledger-tool.mjs [validate|test|check] [ledger.json]");
  }
  const ledger = JSON.parse(await readFile(path || new URL("./ledger.json", import.meta.url), "utf8"));
  const errors = validateLedger(ledger);
  if (errors.length) throw new Error(errors.join("\n"));
  let result;
  if (command === "test") result = await runLedgerTests(ledger);
  else if (command === "check") {
    const observedAt = new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
    result = await checkUpstream(ledger, (url, options) => fetch(url, {
      ...options, signal: AbortSignal.timeout(15000),
    }), observedAt, process.env.GITHUB_TOKEN);
    if (result.results.some(r => r.error || r.evidence_conflicts.length)) process.exitCode = 1;
  } else result = { valid: true, observed_at: ledger.observed_at,
    records: ledger.records.map(record => summarizeRecord(record, ledger)) };
  process.stdout.write(JSON.stringify(result, null, 2) + "\n");
}
main().catch(error => {
  process.stderr.write(error.message + "\n");
  process.exitCode = 1;
});
