// 直调 redbook 内部 XhsClient.getBoardNotes，看 board API 的真实返回
import { XhsClient } from "file:///C:/Users/chens/AppData/Roaming/npm/node_modules/@lucasygu/redbook/dist/lib/client.js";

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
const _here = dirname(fileURLToPath(import.meta.url));
const _cfg = join(_here, "..", "..", "..", "..", ".opencode", "skills", "travel-planner", "config.json");
const cookieStr = JSON.parse(readFileSync(_cfg, "utf8")).redbook_cookie;
const cookies = Object.fromEntries(
  cookieStr.split("; ").map((p) => {
    const i = p.indexOf("=");
    return [p.slice(0, i), p.slice(i + 1)];
  })
);

const client = new XhsClient(cookies);

async function main() {
  const boardId = "6a52494f0000000036010c6e";
  try {
    const data = await client.getBoardNotes(boardId, 30, "");
    console.log("SUCCESS board/note:");
    console.log(JSON.stringify(data).slice(0, 1500));
  } catch (e) {
    console.log("FAILED board/note:", e.name, e.message);
    if (e.response) {
      console.log("response status:", e.response.status);
      try {
        const t = await e.response.text();
        console.log("response body:", t.slice(0, 500));
      } catch (_) {}
    }
    if (e.code !== undefined) console.log("code:", e.code);
  }
  try {
    const info = await client.getBoardInfo(boardId);
    console.log("\nSUCCESS board/info:");
    console.log(JSON.stringify(info).slice(0, 800));
  } catch (e) {
    console.log("\nFAILED board/info:", e.name, e.message, "code:", e.code);
  }
}
main();
