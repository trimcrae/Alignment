// Produced by OpenAI Codex (AI agent, GPT-6); human review not performed.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {validateEvidence} from './core.mjs';
import {runRegressionChecks} from './tests.mjs';
const root = new URL('./', import.meta.url);
const read = path => readFileSync(new URL(path, root), 'utf8');
const evidence = JSON.parse(read('evidence.json'));
const receipt = JSON.parse(read('evidence/acquisition.json'));
const githubCommit = JSON.parse(read('evidence/github-initial-commit.json'));
const readme = read('evidence/initial-readme.md');
const bytes = Buffer.from(readme);
const gitBlobSha = createHash('sha1').update(Buffer.from('blob ' + bytes.length + '\0')).update(bytes).digest('hex');
const command = process.argv[2];
if (command === 'validate' || command === 'summary') {
  console.log(JSON.stringify(validateEvidence(evidence, receipt, readme, gitBlobSha, githubCommit), null, 2));
} else if (command === 'test') {
  console.log(JSON.stringify(runRegressionChecks(evidence, receipt, readme, gitBlobSha, githubCommit), null, 2));
} else if (command === 'hashes') {
  console.log(JSON.stringify(Object.fromEntries(['collect.py', 'acquisition-plan.json', 'core.mjs', 'tests.mjs', 'tool.mjs', 'evidence.json', 'evidence/acquisition.json', 'evidence/initial-readme.md', 'evidence/github-initial-commit.json'].map(path => [path, createHash('sha256').update(readFileSync(new URL(path, root))).digest('hex')])), null, 2));
} else {
  throw new Error('Expected validate, test, summary or hashes');
}
