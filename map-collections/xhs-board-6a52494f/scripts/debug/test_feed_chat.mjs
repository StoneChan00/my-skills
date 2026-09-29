// 用 redbook 内部 client 尝试以 chat 上下文读取越南笔记（无 token 变体测试）
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

// 测试笔记: Little Hanoi Egg (69d484a1000000000b001bb9)
const noteId = "69d484a1000000000b001bb9";

const variants = [
  { xsec_source: "pc_chat", xsec_token: "" },
  { xsec_source: "pc_share", xsec_token: "" },
  { xsec_source: "pc_feed", xsec_token: "" },
];

for (const v of variants) {
  try {
    const data = await client.mainApiPost("/api/sns/web/v1/feed", {
      source_note_id: noteId,
      image_formats: ["jpg", "webp", "avif"],
      extra: { need_body_topic: 1 },
      xsec_source: v.xsec_source,
      xsec_token: v.xsec_token,
    });
    const items = data?.items || [];
    const note = items[0]?.note_card || {};
    console.log(`[${v.xsec_source}] SUCCESS! title=`, note.title || JSON.stringify(data).slice(0, 150));
    break;
  } catch (e) {
    console.log(`[${v.xsec_source}] FAIL:`, String(e.message).slice(0, 100));
  }
}
