// Produced by OpenAI Codex (AI agent, GPT-6); human review not performed.
// This validator covers one bounded evidence snapshot, not arbitrary semantic inference.
const fail = message => { throw new Error(message); };
const object = (v, name) => {
  if (!v || typeof v !== 'object' || Array.isArray(v)) fail(name + ': expected object');
};
const exactKeys = (v, keys, name) => {
  object(v, name);
  if (Object.keys(v).sort().join('|') !== [...keys].sort().join('|')) fail(name + ': unexpected/missing fields');
};
const nonempty = (v, name) => { if (typeof v !== 'string' || !v.trim()) fail(name + ': expected text'); };
const same = (a, b, name) => { if (a !== b) fail(name + ': mismatch'); };
const timestamp = (v, name) => {
  if (typeof v !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(v) || new Date(v).toISOString().replace('.000Z', 'Z') !== v) fail(name + ': invalid UTC timestamp');
};
const sha = (v, length, name) => { if (typeof v !== 'string' || !new RegExp('^[a-f0-9]{' + length + '}$').test(v)) fail(name + ': invalid digest'); };

export function validateEvidence(e, receipt, readme, actualGitBlobSha, githubCommit) {
  exactKeys(e, ['schema_version', 'authorship', 'scope', 'acquisition', 'github_source', 'findings', 'stop'], 'root');
  same(e.schema_version, 1, 'schema');
  same(e.authorship.agent, 'OpenAI Codex', 'AI provenance');
  same(e.authorship.human_review, 'not_performed', 'human review');
  same(e.authorship.base_commit, 'baec2cd33fd25b14127656063a097f64d8ff079e', 'prior ledger base');
  same(JSON.stringify(e.scope.model_ids), JSON.stringify(['openai-gpt-oss-120b', 'openai-gpt-oss-20b']), 'model scope');
  same(e.scope.artifact_id, 'gpt-oss-model-card', 'artifact scope');
  const a = e.acquisition;
  exactKeys(a, ['path', 'source_commit', 'run_id', 'job_id', 'run_url', 'collected_at'], 'acquisition');
  same(a.path, 'evidence/acquisition.json', 'receipt path');
  same(a.source_commit, receipt.execution.source_commit, 'source revision');
  same(a.run_id, receipt.execution.run_id, 'acquisition run');
  same(a.run_url, 'https://github.com/trimcrae/Alignment/actions/runs/' + a.run_id, 'run URL');
  same(a.job_id, '110649236702', 'original job');
  same(a.collected_at, receipt.execution.collected_at, 'acquisition time');
  timestamp(a.collected_at, 'acquisition time');
  const expected = new Map([
    ['official-launch-announcement', ['provider_announcement', 'https://openai.com/index/introducing-gpt-oss/', 'not_fetched', 403]],
    ['arxiv-model-card-record', ['repository_metadata', 'https://arxiv.org/abs/2508.10925', 'observed', 200]],
    ['official-model-card-landing', ['current_landing_page', 'https://openai.com/index/gpt-oss-model-card', 'not_fetched', 403]],
    ['launch-window-card-cdx', ['archive_index_only', 'https://web.archive.org/cdx/search/cdx?url=openai.com%2Findex%2Fgpt-oss-model-card%2A&from=20250804&to=20250807&output=json&filter=statuscode%3A200&fl=timestamp,original,mimetype,statuscode,digest&limit=25', 'not_fetched', 503]],
  ]);
  if (!Array.isArray(receipt.sources) || receipt.sources.length !== expected.size) fail('source coverage');
  const sources = new Map();
  for (const s of receipt.sources) {
    if (sources.has(s.id) || !expected.has(s.id)) fail('duplicate/unexpected source');
    sources.set(s.id, s);
    const [kind, url, state, code] = expected.get(s.id);
    same(s.kind, kind, 'source kind');
    same(s.requested_url, url, 'fixed source URL');
    same(s.state, state, 'observed attempt state');
    same(state === 'observed' ? s.response.status : s.http_status, code, 'HTTP status');
    same(s.robots.allowed, true, 'robots decision');
    timestamp(s.observed_at, 'attempt observation');
    if (state === 'not_fetched') nonempty(s.reason, 'failed fetch reason');
    else { sha(s.received_byte_sha256, 64, 'received HTML hash'); if (!Number.isInteger(s.bytes) || s.bytes <= 0) fail('received bytes'); }
  }
  const g = e.github_source;
  same(g.commit_sha, githubCommit.sha, 'Git commit receipt binding');
  same(g.tree_sha, githubCommit.tree.sha, 'Git tree receipt binding');
  same(g.author_date, githubCommit.author.date, 'author-date receipt binding');
  same(g.committer_date, githubCommit.committer.date, 'committer-date receipt binding');
  same(g.parent_count, githubCommit.parents.length, 'parent receipt binding');
  same(g.signature.verified, githubCommit.verification.verified, 'signature receipt binding');
  same(g.signature.reason, githubCommit.verification.reason, 'signature-reason receipt binding');
  same(g.signature.verified_at, githubCommit.verification.verified_at, 'signature-time receipt binding');
  same(g.id, 'official-initial-readme', 'Git source ID');
  same(g.authority, 'official_provider_repository', 'Git source authority');
  same(g.source_url, 'https://github.com/openai/gpt-oss/blob/' + g.commit_sha + '/README.md', 'Git source URL');
  same(g.preserved_file, 'evidence/initial-readme.md', 'Git copy path');
  sha(g.commit_sha, 40, 'Git commit');
  sha(g.tree_sha, 40, 'Git tree');
  same(g.git_blob_sha, actualGitBlobSha, 'preserved raw README Git hash');
  same(g.parent_count, 0, 'initial commit parents');
  timestamp(g.author_date, 'author date'); timestamp(g.committer_date, 'committer date');
  timestamp(g.receipt_recorded_at, 'Git receipt time');
  same(g.signature.verified, true, 'Git signature');
  same(g.signature.reason, 'valid', 'Git signature reason');
  timestamp(g.signature.verified_at, 'signature verification time');
  nonempty(g.timestamp_limit, 'Git public visibility limitation');
  nonempty(g.receipt_time_meaning, 'recorded-time limitation');
  if (typeof readme !== 'string') fail('raw README text');
  for (const name of ['gpt-oss-120b', 'gpt-oss-20b']) if (!readme.includes(name)) fail('README model identity');
  const f = e.findings;
  exactKeys(f, ['arxiv_submission', 'repository_release_statement', 'repository_card_pointer', 'model_release_date', 'model_card_at_release'], 'findings');
  const x = f.arxiv_submission, s = sources.get('arxiv-model-card-record');
  exactKeys(x, ['status', 'date_kind', 'timestamp', 'precision', 'version', 'citation'], 'arXiv finding');
  same(x.status, 'reported', 'arXiv status'); same(x.date_kind, 'repository_submission_metadata', 'arXiv date kind');
  same(x.precision, 'second', 'arXiv precision');
  exactKeys(x.citation, ['source_id', 'received_byte_sha256', 'quote'], 'arXiv citation');
  same(x.citation.source_id, s.id, 'arXiv source binding');
  same(x.citation.received_byte_sha256, s.received_byte_sha256, 'arXiv received hash');
  nonempty(x.citation.quote, 'arXiv quote');
  if (!s.extraction.spans.some(span => span.text.includes(x.citation.quote))) fail('quote not in acquired selected span');
  const match = /^\[(v\d+)\] [A-Za-z]{3}, (\d{1,2}) ([A-Za-z]{3}) (\d{4}) (\d{2}:\d{2}:\d{2}) UTC \([\d,]+ KB\)$/.exec(x.citation.quote);
  if (!match) fail('native arXiv submission history syntax');
  same(x.version, match[1], 'arXiv version');
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const month = months.indexOf(match[3]) + 1;
  if (!month) fail('arXiv month');
  same(x.timestamp, match[4] + '-' + String(month).padStart(2, '0') + '-' + match[2].padStart(2, '0') + 'T' + match[5] + 'Z', 'native submission timestamp');
  timestamp(x.timestamp, 'arXiv time');
  const gitCitation = c => {
    exactKeys(c, ['source_id', 'git_blob_sha', 'quote'], 'Git citation');
    same(c.source_id, g.id, 'Git citation source'); same(c.git_blob_sha, g.git_blob_sha, 'Git citation hash');
    nonempty(c.quote, 'Git quote'); if (!readme.includes(c.quote)) fail('Git quote not in preserved raw source');
  };
  const r = f.repository_release_statement;
  exactKeys(r, ['status', 'date_kind', 'timestamp', 'precision', 'citation', 'interpretation'], 'repository statement');
  same(r.status, 'reported', 'repository statement status'); same(r.date_kind, 'git_committer_metadata', 'repository date kind');
  same(r.timestamp, g.committer_date, 'Git metadata time'); same(r.precision, 'second', 'Git precision');
  gitCitation(r.citation); same(r.citation.quote, "We're releasing two flavors of the open models:", 'releasing quote');
  nonempty(r.interpretation, 'Git statement limitation');
  const p = f.repository_card_pointer;
  exactKeys(p, ['status', 'citation', 'linked_url', 'edition_binding', 'interpretation'], 'repository pointer');
  same(p.status, 'reported', 'pointer status'); gitCitation(p.citation);
  same(p.linked_url, 'https://openai.com/index/gpt-oss-model-card', 'official card link');
  if (!p.citation.quote.includes('href="' + p.linked_url + '"')) fail('card URL not quoted');
  same(p.edition_binding, 'none', 'pointer edition limitation'); nonempty(p.interpretation, 'pointer limitation');
  exactKeys(f.model_release_date, ['status', 'value', 'reason'], 'actual release');
  same(f.model_release_date.status, 'unknown', 'unsupported actual release date');
  same(f.model_release_date.value, null, 'unknown release value'); nonempty(f.model_release_date.reason, 'release missing evidence');
  exactKeys(f.model_card_at_release, ['status', 'edition', 'received_byte_sha256', 'reason'], 'launch edition');
  same(f.model_card_at_release.status, 'unknown', 'unsupported launch availability');
  same(f.model_card_at_release.edition, null, 'unknown launch edition');
  same(f.model_card_at_release.received_byte_sha256, null, 'no historical byte binding');
  nonempty(f.model_card_at_release.reason, 'launch missing evidence');
  same(e.stop.state, 'complete_missing_evidence', 'bounded stop state');
  same(e.stop.cycles, 1, 'one acquisition cycle'); same(e.stop.retry_performed, false, 'no retries');
  same(e.stop.pdf_reacquired, false, 'no PDF reacquisition'); nonempty(e.stop.remaining_gap, 'explicit gap');
  return {reported_submission_timestamp: x.timestamp, repository_commit_timestamp: r.timestamp, model_release_date: 'unknown', launch_edition: 'unknown', sources_observed: 1, sources_not_fetched: 3};
}
