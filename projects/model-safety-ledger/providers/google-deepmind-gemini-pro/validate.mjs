#!/usr/bin/env node
// AI-authored OpenAI Codex/GPT-6. Actual Node CLI hashes original retained bytes.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {validate} from "./core.mjs";
const root=dirname(fileURLToPath(import.meta.url));
export function loadBundle(){return Object.fromEntries(Object.entries({original_receipt:"acquisition.json",landing_selected:"landing-selected.json",card_receipt:"card-acquisition.json",landing_received:"landing.html",robots_received:"robots-deepmind.google.txt"}).map(([k,f])=>[k,readFileSync(join(root,"evidence",f))]));}
export const digest=x=>createHash("sha256").update(x).digest("hex");
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const result=JSON.parse(readFileSync(join(root,"result.json"),"utf8"));
 console.log(JSON.stringify(validate(result,loadBundle(),digest),null,2));
}
