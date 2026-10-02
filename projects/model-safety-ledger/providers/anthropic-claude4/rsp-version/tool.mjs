// Produced by OpenAI Codex (AI agent, GPT-6). Human review not performed.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {validate,summarize} from "./core.mjs";
import {runTests} from "./tests.mjs";
const root=dirname(fileURLToPath(import.meta.url)),hash=s=>createHash("sha256").update(s,"utf8").digest("hex");
const result=JSON.parse(readFileSync(join(root,"result.json"),"utf8")),receipt=readFileSync(join(root,"evidence/acquisition.json"),"utf8"),prior=readFileSync(join(root,"../ledger.json"),"utf8");
const mode=process.argv[2];
if(mode==="validate"){const got=validate(result,JSON.parse(receipt),hash(receipt),hash(prior));console.log(JSON.stringify(got,null,2));if(!got.valid)process.exitCode=1;}
else if(mode==="test")console.log(JSON.stringify(runTests(result,receipt,hash,hash(prior)),null,2));
else if(mode==="summary"){const got=validate(result,JSON.parse(receipt),hash(receipt),hash(prior));if(!got.valid)throw Error(got.errors.join("; "));console.log(JSON.stringify(summarize(result),null,2));}
else throw Error("Usage: node tool.mjs validate|test|summary");
