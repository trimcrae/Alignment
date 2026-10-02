// Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {validate,summarize} from "./core.mjs";
import {runTests} from "./tests.mjs";
const root=dirname(fileURLToPath(import.meta.url));
const ledger=JSON.parse(readFileSync(join(root,"ledger.json"),"utf8"));
const receiptText=readFileSync(join(root,"evidence/primary-acquisition.json"),"utf8");
const digest=s=>createHash("sha256").update(s,"utf8").digest("hex");
const mode=process.argv[2];
if(mode==="validate"){const result=validate(ledger,JSON.parse(receiptText),digest(receiptText));console.log(JSON.stringify(result,null,2));if(!result.valid)process.exitCode=1;}
else if(mode==="test")console.log(JSON.stringify(runTests(ledger,receiptText,digest),null,2));
else if(mode==="summary"){const result=validate(ledger,JSON.parse(receiptText),digest(receiptText));if(!result.valid)throw Error(result.errors.join("; "));console.log(JSON.stringify(summarize(ledger),null,2));}
else throw Error("Usage: node tool.mjs validate|test|summary");
