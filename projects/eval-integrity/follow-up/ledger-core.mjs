// Produced by OpenAI Codex (AI agent), usage-sprint-2026-10-01.
// Pure validation and read-only observation logic; no filesystem or network globals.

const SHA = /^[0-9a-f]{40}$/;
const REPO = /^[A-Za-z0-9][A-Za-z0-9-]*\/[A-Za-z0-9_.-]+$/;
const ID = /^[a-z][a-z0-9-]*$/;
const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
const nonempty = value => typeof value === "string" && value.trim().length > 0;
const timestamp = value => typeof value === "string" &&
  /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(value) &&
  Number.isFinite(Date.parse(value)) && new Date(value).toISOString() === value.replace("Z", ".000Z");
const integer = value => Number.isSafeInteger(value) && value > 0;
const githubLink = value => typeof value === "string" && /^https:\/\/github\.com\/[A-Za-z0-9][A-Za-z0-9-]*\/[A-Za-z0-9_.-]+\/(?:blob|issues|pull)\//.test(value);

export function resourceUrls(resource) {
  const { repository, kind, data: d } = resource;
  if (!REPO.test(repository) || [".", ".."].includes(repository.split("/")[1]) || !object(d)) {
    throw new Error("Invalid repository or resource data");
  }
  const api = "https://api.github.com/repos/" + repository;
  const html = "https://github.com/" + repository;
  switch (kind) {
    case "repository": return { api, html };
    case "issue": return { api: api + "/issues/" + d.number, html: html + "/issues/" + d.number };
    case "pull-request": return { api: api + "/pulls/" + d.number, html: html + "/pull/" + d.number };
    case "review": return {
      api: api + "/pulls/" + d.pull_number + "/reviews",
      html: html + "/pull/" + d.pull_number + "#pullrequestreview-" + d.id,
    };
    case "comparison": return {
      api: api + "/compare/" + d.base_sha + "..." + d.head_sha,
      html: html + "/compare/" + d.base_sha + "..." + d.head_sha,
    };
    case "file": {
      if (!nonempty(d.path) || !/^[A-Za-z0-9_./-]+$/.test(d.path) ||
          d.path.startsWith("/") || d.path.split("/").some(part => ["", ".", ".."].includes(part))) {
        throw new Error("Invalid repository file path");
      }
      return {
        api: api + "/contents/" + d.path + "?ref=" + d.commit_sha,
        html: html + "/blob/" + d.commit_sha + "/" + d.path,
      };
    }
    default: throw new Error("Unknown resource kind");
  }
}

export function validateLedger(ledger) {
  const errors = [];
  const require = (ok, message) => { if (!ok) errors.push(message); };
  require(object(ledger), "ledger must be an object");
  if (!object(ledger)) return errors;
  require(ledger.schema_version === 1, "schema_version must be 1");
  require(timestamp(ledger.observed_at), "observed_at must be a real UTC timestamp");
  const p = ledger.provenance;
  require(object(p) && nonempty(p.author) && /AI agent/.test(p.author) && nonempty(p.session) &&
    REPO.test(p.repository) && SHA.test(p.base_commit) && SHA.test(p.prior_triage_commit) &&
    nonempty(p.verification), "provenance must identify AI authorship, session, repository, commits and verification");
  require(Array.isArray(ledger.resources) && ledger.resources.length > 0, "resources must be nonempty");
  require(Array.isArray(ledger.records) && ledger.records.length > 0, "records must be nonempty");
  if (!Array.isArray(ledger.resources) || !Array.isArray(ledger.records)) return errors;
  const resources = new Map();
  for (const r of ledger.resources) {
    if (!object(r)) { errors.push("resource must be an object"); continue; }
    const label = "resource " + String(r.key);
    require(typeof r.key === "string" && ID.test(r.key) && !resources.has(r.key), label + ": unique slug required");
    resources.set(r.key, r);
    require(timestamp(r.observed_at) && r.observed_at <= ledger.observed_at, label + ": observation exceeds snapshot or is invalid");
    if (!object(r.data)) { errors.push(label + ": data must be an object"); continue; }
    const d = r.data;
    try {
      const urls = resourceUrls(r);
      require(r.api_url === urls.api && r.html_url === urls.html, label + ": canonical URLs required");
    } catch (error) { errors.push(label + ": " + error.message); }
    if (r.kind === "repository") require(nonempty(d.default_branch), label + ": default branch required");
    if (r.kind === "issue" || r.kind === "pull-request") {
      require(integer(d.number) && nonempty(d.title), label + ": number and title required");
      require(["open", "closed"].includes(d.state), label + ": invalid state");
      require(timestamp(d.updated_at) && d.updated_at <= r.observed_at, label + ": invalid update time");
      require(d.closed_at === null || (timestamp(d.closed_at) && d.closed_at <= d.updated_at), label + ": invalid closure time");
      require((d.state === "closed") === (d.closed_at !== null), label + ": state and closure disagree");
    }
    if (r.kind === "pull-request") {
      require(typeof d.draft === "boolean" && typeof d.merged === "boolean", label + ": draft/merged must be boolean");
      require(nonempty(d.base_ref) && SHA.test(d.base_sha) && SHA.test(d.head_sha), label + ": exact target ref and SHAs required");
      require(d.merged ? d.state === "closed" && timestamp(d.merged_at) && d.merged_at <= d.updated_at &&
        SHA.test(d.merge_commit_sha) : d.merged_at === null && d.merge_commit_sha === null, label + ": inconsistent merge evidence");
    }
    if (r.kind === "review") {
      require(integer(d.id) && integer(d.pull_number) && nonempty(d.author) && nonempty(d.quote) &&
        timestamp(d.submitted_at) && d.submitted_at <= r.observed_at && SHA.test(d.commit_id),
      label + ": review identity, quote, timestamp and reviewed commit required");
    }
    if (r.kind === "comparison") {
      require(SHA.test(d.base_sha) && SHA.test(d.head_sha) && SHA.test(d.merge_base_sha), label + ": exact comparison SHAs required");
      require(["ahead", "behind", "identical", "diverged"].includes(d.status) &&
        Number.isSafeInteger(d.ahead_by) && d.ahead_by >= 0 &&
        Number.isSafeInteger(d.behind_by) && d.behind_by >= 0, label + ": invalid ancestry result");
    }
    if (r.kind === "file") {
      require(SHA.test(d.commit_sha) && SHA.test(d.blob_sha) && nonempty(d.excerpt), label + ": pinned source and excerpt required");
    }
  }
  const ids = new Set();
  const lookup = (key, kinds, label) => {
    const r = resources.get(key);
    require(r && kinds.includes(r.kind) && object(r.data), label + ": missing or wrong-kind receipt " + key);
    return r && kinds.includes(r.kind) && object(r.data) ? r : undefined;
  };
  for (const record of ledger.records) {
    if (!object(record)) { errors.push("record must be an object"); continue; }
    const label = "record " + String(record.id);
    require(typeof record.id === "string" && ID.test(record.id) && !ids.has(record.id), label + ": unique slug required");
    ids.add(record.id);
    require(nonempty(record.title) && nonempty(record.next_action) && githubLink(record.prior_artifact), label + ": title, next action and prior artifact required");
    require(["reported", "duplicate", "pending-owner-review"].includes(record.scope), label + ": invalid scope");
    require(record.release_status === "not-checked", label + ": this schema does not establish release inclusion");
    const issue = record.issue === null ? null : lookup(record.issue, ["issue"], label);
    require(Array.isArray(record.pull_requests), label + ": pull_requests must be an array");
    const pulls = Array.isArray(record.pull_requests) ? record.pull_requests.map(key => lookup(key, ["pull-request"], label)).filter(Boolean) : [];
    require(Array.isArray(record.pull_requests) && new Set(record.pull_requests).size === pulls.length, label + ": duplicate or missing pull receipt");
    const repo = issue?.repository || pulls[0]?.repository;
    require(nonempty(repo) && pulls.every(r => r.repository === repo), label + ": related receipts must belong to one repository");
    if (record.scope === "reported") require(issue && issue.repository !== p?.repository, label + ": reported finding needs upstream issue");
    if (record.scope === "duplicate") require(pulls.length > 0 && record.issue === null, label + ": duplicate uses existing PR, without a new issue");
    if (record.scope === "pending-owner-review") require(issue && issue.repository === p?.repository && pulls.length === 0,
      label + ": pending-owner-review uses a local issue without upstream PR");
    if (record.confirmation) {
      const review = lookup(record.confirmation, ["review"], label);
      const pull = review && pulls.find(r => r.data.number === review.data.pull_number && r.repository === review.repository);
      require(review && pull && ["OWNER", "MEMBER", "COLLABORATOR"].includes(review.data.author_association) &&
        review.data.state === "APPROVED" && review.data.commit_id === pull.data.head_sha,
      label + ": confirmation must be a linked collaborator approval of the exact head");
      // A reviewer must read the quote; approval alone does not establish bug confirmation.
      require(review && /\bconfirmed\b/i.test(review.data.quote) && /\bbug\b/i.test(review.data.quote) && /\bfix\b/i.test(review.data.quote),
        label + ": explicit bug-and-fix confirmation quote required");
    }
    if (record.default_branch !== undefined) {
      const branch = record.default_branch;
      if (!object(branch)) { errors.push(label + ": default_branch must be an object"); continue; }
      const repository = lookup(branch.repository, ["repository"], label);
      const pull = lookup(branch.pull_request, ["pull-request"], label);
      const comparison = lookup(branch.ancestry, ["comparison"], label);
      const source = lookup(branch.source, ["file"], label);
      require(repository && repository.repository === repo && repository.data.default_branch === branch.name &&
        pulls.includes(pull) && pull?.data.merged === true && pull?.data.base_ref === branch.name,
        label + ": default branch needs a merged PR targeting its exact name");
      require(comparison && source && pull && comparison.repository === repo && source.repository === repo &&
        comparison.data.base_sha === pull.data.merge_commit_sha &&
        comparison.data.head_sha === source.data.commit_sha &&
        comparison.data.merge_base_sha === comparison.data.base_sha &&
        ["ahead", "identical"].includes(comparison.data.status) && comparison.data.behind_by === 0,
      label + ": default inclusion needs matching ancestry and independently pinned source");
    }
  }
  return errors;
}

export function summarizeRecord(record, ledger) {
  const errors = validateLedger(ledger);
  if (errors.length) throw new Error(errors.join("\n"));
  if (!ledger.records.includes(record)) throw new Error("Record must belong to this validated ledger");
  const map = new Map(ledger.resources.map(r => [r.key, r]));
  let status;
  if (record.scope === "pending-owner-review") status = "owner review pending; no upstream report recorded";
  else if (record.default_branch) status = "fix included in " + record.default_branch.name + " at pinned source";
  else if (record.scope === "duplicate") status = "duplicate; existing upstream PR " + map.get(record.pull_requests[0]).data.state;
  else {
    const pulls = record.pull_requests.map(key => map.get(key));
    const merged = pulls.find(r => r.data.merged);
    if (merged) status = "merged into " + merged.data.base_ref + "; default inclusion not established";
    else if (pulls.length) status = pulls.map(r => "PR #" + r.data.number + " " + r.data.state + (r.data.draft ? " (draft)" : "")).join("; ");
    else status = "upstream issue " + map.get(record.issue).data.state + "; no fix PR recorded";
  }
  return { id: record.id, status, maintainer_confirmation: Boolean(record.confirmation), release_status: record.release_status };
}

export function normalizeObservation(resource, payload, observedAt) {
  if (!["issue", "pull-request"].includes(resource.kind)) throw new Error("Only issue/PR state is refreshed");
  if (!object(payload) || payload.html_url !== resource.html_url || payload.number !== resource.data.number ||
      (resource.kind === "issue" && payload.pull_request)) throw new Error("Response identity or resource kind mismatch");
  const data = {
    number: payload.number, title: payload.title, state: payload.state,
    updated_at: payload.updated_at, closed_at: payload.closed_at,
  };
  if (resource.kind === "issue") data.state_reason = payload.state_reason;
  else Object.assign(data, {
    draft: payload.draft, merged: payload.merged, merged_at: payload.merged_at,
    base_ref: payload.base?.ref, base_sha: payload.base?.sha, head_sha: payload.head?.sha,
    merge_commit_sha: payload.merged ? payload.merge_commit_sha : null,
  });
  return { ...resource, observed_at: observedAt, data };
}

export async function checkUpstream(ledger, fetcher, observedAt, token) {
  const errors = validateLedger(ledger);
  if (errors.length) throw new Error(errors.join("\n"));
  if (!timestamp(observedAt) || observedAt < ledger.observed_at) throw new Error("Invalid or backward observation time");
  const results = [];
  for (const resource of ledger.resources.filter(r => ["issue", "pull-request"].includes(r.kind))) {
    try {
      const headers = { Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "Alignment-follow-up-ledger" };
      if (token) headers.Authorization = "Bearer " + token;
      const response = await fetcher(resource.api_url, { method: "GET", headers, redirect: "error" });
      if (!response.ok) throw new Error("GitHub HTTP " + response.status);
      const current = normalizeObservation(resource, await response.json(), observedAt);
      const candidate = { ...ledger, observed_at: observedAt, resources: ledger.resources.map(r => r.key === resource.key ? current : r) };
      const problems = validateLedger(candidate);
      const resourceProblems = problems.filter(problem => problem.startsWith("resource " + resource.key + ":"));
      if (resourceProblems.length) throw new Error(resourceProblems.join("; "));
      results.push({
        key: resource.key, url: resource.html_url, observed_at: observedAt,
        changed_fields: Object.keys(current.data).filter(key => JSON.stringify(current.data[key]) !== JSON.stringify(resource.data[key])),
        current: current.data,
        evidence_conflicts: problems,
      });
    } catch (error) {
      // Do not include response bodies or authentication headers in the report.
      results.push({ key: resource.key, url: resource.html_url, error: token ? String(error.message).split(token).join("[REDACTED]") : error.message });
    }
  }
  return { observed_at: observedAt, snapshot_observed_at: ledger.observed_at,
    scope: "Issue and PR state only; confirmation, ancestry, source and releases were not refreshed.", results };
}
