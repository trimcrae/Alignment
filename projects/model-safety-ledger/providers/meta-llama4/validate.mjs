#!/usr/bin/env node
// AI-authored OpenAI Codex/GPT-6: actual Node hashes original retained byte objects.
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
import {dirname,join} from "node:path";
import {validate} from "./core.mjs";
const root=dirname(fileURLToPath(import.meta.url));
export function loadBundle(){return Object.fromEntries(Object.entries({card:"evidence/MODEL_CARD.md",tool:"evidence/original-tool-receipt.json",citations:"evidence/citations.json",acquisition:"evidence/acquisition.json",plan:"acquisition-plan.json"}).map(([k,p])=>[k,readFileSync(join(root,p))]));}
export const deps={sha256:x=>createHash("sha256").update(x).digest("hex"),gitBlobSha1:x=>createHash("sha1").update(Buffer.concat([Buffer.from("blob "+x.length+"\0"),x])).digest("hex"),decodeBase64:x=>Buffer.from(x,"base64"),byteLength:x=>x.length,byteSlice:(x,a,b)=>x.subarray(a,b).toString("utf8")};
if(process.argv[1]===fileURLToPath(import.meta.url)){const r=JSON.parse(readFileSync(join(root,"result.json"),"utf8"));console.log(JSON.stringify(validate(r,loadBundle(),deps),null,2));}
