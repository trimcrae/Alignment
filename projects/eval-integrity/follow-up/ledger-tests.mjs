// Produced by OpenAI Codex (AI agent), usage-sprint-2026-10-01.
// These cases exercise evidence inflation, stale observations and failed network reads.
import { validateLedger, summarizeRecord, normalizeObservation, checkUpstream } from "./ledger-core.mjs";

export async function runLedgerTests(fixture) {
  const names = [];
  const clone = value => JSON.parse(JSON.stringify(value));
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const equal = (actual, expected) => assert(JSON.stringify(actual) === JSON.stringify(expected),
    "Expected " + JSON.stringify(expected) + ", got " + JSON.stringify(actual));
  const test = async (name, fn) => { await fn(); names.push(name); };
  const invalid = (mutate, fragment) => {
    const ledger = clone(fixture); mutate(ledger);
    const errors = validateLedger(ledger);
    assert(errors.some(error => error.includes(fragment)), "Missing error " + fragment + ": " + errors.join("; "));
  };
  const resource = (ledger, key) => ledger.resources.find(r => r.key === key);
  const record = ledger => ledger.records.find(r => r.id === "controlarena-judge-failure");
  const future = new Date(Date.parse(fixture.observed_at) + 86400000).toISOString().replace(".000Z", "Z");
  const liveCount = fixture.resources.filter(r => ["issue", "pull-request"].includes(r.kind)).length;
  const payload = r => {
    const p = { ...clone(r.data), html_url: r.html_url };
    if (r.kind === "pull-request") {
      p.base = { ref: p.base_ref, sha: p.base_sha };
      p.head = { sha: p.head_sha };
    }
    return p;
  };
  const fetcher = (ledger, transform = r => payload(r)) => async (url, options) => {
    assert(options.method === "GET" && options.redirect === "error", "Read-only method and rejected redirects required");
    const r = ledger.resources.find(r => r.api_url === url);
    assert(r && ["issue", "pull-request"].includes(r.kind), "Only known issue and pull endpoints may be read");
    return { ok: true, status: 200, json: async () => transform(r) };
  };
  await test("real receipt fixture validates without mutation", () => {
    const before = JSON.stringify(fixture);
    equal(validateLedger(fixture), []);
    equal(JSON.stringify(fixture), before);
  });
  await test("six real follow-ups produce separate status dimensions", () => {
    equal(summarizeRecord(record(fixture), fixture), {
      id: "controlarena-judge-failure", status: "fix included in main at pinned source",
      maintainer_confirmation: true, release_status: "not-checked",
    });
    assert(summarizeRecord(fixture.records.find(r => r.scope === "duplicate"), fixture).status.startsWith("duplicate"), "Duplicate route");
    assert(summarizeRecord(fixture.records.find(r => r.scope === "pending-owner-review"), fixture).status.includes("no upstream report"), "Local review route");
  });
  await test("intermediate merge does not imply default branch or release", () => {
    const ledger = clone(fixture); delete record(ledger).default_branch;
    const summary = summarizeRecord(record(ledger), ledger);
    assert(summary.status.includes("rogan-inglis/fix/sae-judge-noanswer"), "Exact intermediate branch retained");
    assert(summary.status.includes("default inclusion not established"), "No implicit main inclusion");
    equal(summary.release_status, "not-checked");
  });
  await test("closed unmerged pull does not imply fixed", () => {
    const ledger = clone(fixture); const r = resource(ledger, "agentharm-pr");
    r.data.state = "closed"; r.data.closed_at = r.data.updated_at;
    equal(validateLedger(ledger), []);
    equal(summarizeRecord(ledger.records[0], ledger).status, "PR #2455 closed");
  });
  await test("merged open pull is contradictory", () => invalid(l => resource(l, "controlarena-pr").data.state = "open", "inconsistent merge evidence"));
  await test("merge requires an exact target ref", () => invalid(l => delete resource(l, "controlarena-pr").data.base_ref, "exact target ref"));
  await test("malformed SHAs fail", () => invalid(l => resource(l, "controlarena-main-source").data.commit_sha = "173c872", "pinned source"));
  await test("closure and state must agree", () => invalid(l => resource(l, "agentharm-issue").data.closed_at = l.observed_at, "state and closure disagree"));
  await test("future observation is rejected", () => invalid(l => resource(l, "agentharm-issue").observed_at = future, "observation exceeds"));
  await test("invalid calendar day is rejected", () => invalid(l => l.observed_at = "2026-02-30T00:00:00Z", "real UTC timestamp"));
  await test("resource update cannot occur after read", () => invalid(l => resource(l, "agentharm-issue").data.updated_at = future, "invalid update time"));
  await test("canonical API URL forbids alternate origin", () => invalid(l => resource(l, "agentharm-pr").api_url = "https://example.com/token", "canonical URLs"));
  await test("canonical HTML URL binds the issue identity", () => invalid(l => resource(l, "agentharm-issue").html_url = "https://github.com/UKGovernmentBEIS/inspect_evals/issues/1", "canonical URLs"));
  await test("file path traversal is rejected", () => invalid(l => resource(l, "controlarena-main-source").data.path = "../secrets", "Invalid repository file path"));
  await test("duplicate resource keys are rejected", () => invalid(l => l.resources.push(clone(l.resources[0])), "unique slug"));
  await test("unknown resource kinds fail", () => invalid(l => l.resources[0].kind = "release", "Unknown resource kind"));
  await test("missing resource references fail", () => invalid(l => record(l).issue = "missing", "missing or wrong-kind receipt"));
  await test("malformed related pull list fails without throwing", () => invalid(l => record(l).pull_requests = {}, "pull_requests must be an array"));
  await test("null resource data fails without throwing", () => invalid(l => resource(l, "controlarena-pr").data = null, "data must be an object"));
  await test("cross-repository related receipts fail", () => invalid(l => record(l).pull_requests.push("petri-rescore-pr"), "one repository"));
  await test("approval alone is not bug confirmation", () => invalid(l => resource(l, "controlarena-confirmation").data.quote = "Looks good to me", "confirmation quote"));
  await test("noncollaborator approval is not a maintainer receipt", () => invalid(l => resource(l, "controlarena-confirmation").data.author_association = "NONE", "linked collaborator"));
  await test("approval must bind the actual head", () => invalid(l => resource(l, "controlarena-confirmation").data.commit_id = "a".repeat(40), "exact head"));
  await test("default branch metadata must match merge target", () => invalid(l => resource(l, "controlarena-repository").data.default_branch = "master", "exact name"));
  await test("diverged history does not establish default inclusion", () => invalid(l => resource(l, "controlarena-main-ancestry").data.status = "diverged", "matching ancestry"));
  await test("comparison identical requires equal SHAs and zero counts", () => invalid(l => resource(l, "controlarena-main-ancestry").data.status = "identical", "status, counts and merge base disagree"));
  await test("comparison ahead requires positive ahead count", () => invalid(l => resource(l, "controlarena-main-ancestry").data.ahead_by = 0, "status, counts and merge base disagree"));
  await test("source and comparison cannot invent an observed branch head", () => invalid(l => {
    const source = resource(l, "controlarena-main-source");
    const comparison = resource(l, "controlarena-main-ancestry");
    source.data.commit_sha = "a".repeat(40); comparison.data.head_sha = "a".repeat(40);
    source.api_url = source.api_url.replace(/ref=[0-9a-f]{40}$/, "ref=" + "a".repeat(40));
    source.html_url = source.html_url.replace(/blob\/[0-9a-f]{40}\//, "blob/" + "a".repeat(40) + "/");
    comparison.api_url = comparison.api_url.replace(/\.\.\.[0-9a-f]{40}$/, "..." + "a".repeat(40));
    comparison.html_url = comparison.html_url.replace(/\.\.\.[0-9a-f]{40}$/, "..." + "a".repeat(40));
  }, "matching ancestry"));
  await test("merged pull cannot predate closure or remain draft", () => {
    invalid(l => resource(l, "controlarena-pr").data.closed_at = "2026-09-27T00:00:00Z", "inconsistent merge");
    invalid(l => resource(l, "controlarena-pr").data.draft = true, "inconsistent merge");
  });
  await test("ancestry must bind integration PR merge commit", () => invalid(l => resource(l, "controlarena-main-ancestry").data.base_sha = "b".repeat(40), "matching ancestry"));
  await test("release inclusion cannot be inferred", () => invalid(l => record(l).release_status = "released", "does not establish release"));
  await test("duplicate finding cannot silently acquire a new issue", () => invalid(l => l.records.find(r => r.scope === "duplicate").issue = "agentharm-issue", "without a new issue"));
  await test("outside record cannot bypass validated ledger", () => {
    let failed = false; try { summarizeRecord({ ...record(fixture) }, fixture); } catch { failed = true; }
    assert(failed, "Unvalidated record accepted");
  });
  await test("response identity and issue/PR kind are checked", () => {
    const r = resource(fixture, "agentharm-issue");
    for (const p of [{ ...payload(r), number: 1 }, { ...payload(r), pull_request: {} }]) {
      let failed = false; try { normalizeObservation(r, p, future); } catch { failed = true; }
      assert(failed, "Mismatched response accepted");
    }
  });
  await test("read-only refresh preserves original snapshot", async () => {
    const before = JSON.stringify(fixture);
    const report = await checkUpstream(fixture, fetcher(fixture), future);
    equal(report.results.length, liveCount);
    assert(report.results.every(r => !r.error && r.changed_fields.length === 0 && r.evidence_conflicts.length === 0), "Expected unchanged state");
    equal(JSON.stringify(fixture), before);
  });
  await test("changed PR head surfaces stale approval instead of hiding new state", async () => {
    const report = await checkUpstream(fixture, fetcher(fixture, r => {
      const p = payload(r); if (r.key === "controlarena-pr") p.head.sha = "a".repeat(40); return p;
    }), future);
    const result = report.results.find(r => r.key === "controlarena-pr");
    assert(!result.error && result.changed_fields.includes("head_sha"), "Changed state hidden");
    assert(result.evidence_conflicts.some(error => error.includes("exact head")), "Stale confirmation not surfaced");
  });
  await test("HTTP failure is explicit and other reads continue", async () => {
    const good = fetcher(fixture);
    const report = await checkUpstream(fixture, async (url, options) =>
      url === fixture.resources[0].api_url ? { ok: false, status: 403 } : good(url, options), future);
    equal(report.results[0].error, "GitHub HTTP 403");
    equal(report.results.length, liveCount);
    assert(!report.results[1].error, "A failure stopped later receipts");
  });
  await test("malformed live merge evidence does not produce success", async () => {
    const report = await checkUpstream(fixture, fetcher(fixture, r => {
      const p = payload(r); if (r.key === "controlarena-main-pr") p.state = "open"; return p;
    }), future);
    assert(report.results.find(r => r.key === "controlarena-main-pr").error.includes("inconsistent merge"), "Malformed evidence accepted");
  });
  await test("optional token is redacted from fetch errors", async () => {
    const token = "test-token-that-must-not-be-printed";
    const report = await checkUpstream(fixture, async () => { throw new Error("request " + token + " failed"); }, future, token);
    assert(!JSON.stringify(report).includes(token), "Token leaked");
  });
  await test("backward live observation time fails before reads", async () => {
    let called = false; let failed = false;
    try { await checkUpstream(fixture, async () => { called = true; }, "2026-09-01T00:00:00Z"); } catch { failed = true; }
    assert(failed && !called, "Backward snapshot accepted");
  });
  return { passed: names.length, names };
}
