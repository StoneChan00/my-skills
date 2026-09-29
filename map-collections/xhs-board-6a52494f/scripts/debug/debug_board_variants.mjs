// 测试 board/note API 的各种参数组合（share_id 授权 / xsec_source 变体）
import { XhsClient } from "file:///C:/Users/chens/AppData/Roaming/npm/node_modules/@lucasygu/redbook/dist/lib/client.js";

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
const _here = dirname(fileURLToPath(import.meta.url));
const _cfg = join(_here, "..", "..", "..", "..", ".opencode", "skills", "travel-planner", "config.json");
const cookieStr = JSON.parse(readFileSync(_cfg, "utf8")).redbook_cookie;
const cookies = Object.fromEntries(cookieStr.split("; ").map((p) => {
  const i = p.indexOf("=");
  return [p.slice(0, i), p.slice(i + 1)];
}));
const client = new XhsClient(cookies);
const boardId = "6a52494f0000000036010c6e";
const shareId = "555732213bb344888c349407e563b45d";

// 直接用内部 mainApiGet 尝试不同参数
const variants = [
  { board_id: boardId, num: 30, cursor: "", xsec_source: "pc_share", share_id: shareId },
  { board_id: boardId, num: 30, cursor: "", xsec_source: "pc_feed" },
  { board_id: boardId, num: 30, cursor: "", share_id: shareId },
  { board_id: boardId, num: 30, cursor: "", source: "share" },
];

for (const [i, params] of variants.entries()) {
  try {
    const data = await client.mainApiGet("/api/sns/web/v1/board/note", params);
    console.log(`[V${i}] SUCCESS:`, JSON.stringify(params), "=>", JSON.stringify(data).slice(0, 300));
  } catch (e) {
    console.log(`[V${i}] FAIL:`, JSON.stringify(params), "=>", e.message.slice(0, 120));
  }
}

// 也试 v2 版本路径
for (const path of ["/api/sns/web/v2/board/note", "/api/sns/web/v1/board/note_list"]) {
  try {
    const data = await client.mainApiGet(path, { board_id: boardId, num: 30, cursor: "" });
    console.log(`[${path}] SUCCESS =>`, JSON.stringify(data).slice(0, 300));
  } catch (e) {
    console.log(`[${path}] FAIL =>`, e.message.slice(0, 120));
  }
}
