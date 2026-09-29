# -*- coding: utf-8 -*-
"""直接用 cookie 调聊天历史 API（IM 接口免签名），检查新笔记卡片。"""
import json
import re
import urllib.request
from pathlib import Path

BASE = Path(r"D:\2_Projects\github\StoneChan00\my-skills\map-collections\xhs-board-6a52494f")
CFG = Path(r"D:\2_Projects\github\StoneChan00\my-skills\.opencode\skills\travel-planner\config.json")
cookie = json.loads(CFG.read_text(encoding="utf-8"))["redbook_cookie"]

url = ("https://edith.xiaohongshu.com/api/im/web/messages/history?"
       "chat_user_id=61b6c78e000000001000ba5d&last_id=0&start_id=0&limit=100")
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Cookie": cookie,
    "Referer": "https://www.xiaohongshu.com/",
    "Origin": "https://www.xiaohongshu.com",
})
with urllib.request.urlopen(req, timeout=20) as r:
    j = json.loads(r.read().decode("utf-8"))

msgs = (j.get("data") or {}).get("out_message_list") or []
print(f"API ok, messages: {len(msgs)}, maxStoreId: {max((m['store_id'] for m in msgs), default=0)}")

notes = {}
for m in msgs:
    try:
        c = json.loads(m["content"])
    except Exception:
        continue
    if c.get("content_type") != 3:
        continue
    try:
        inner = json.loads(c["content"]) if isinstance(c["content"], str) else (c["content"] or {})
    except Exception:
        continue
    if inner.get("type") != "note" or not inner.get("id"):
        continue
    tok = ""
    link = inner.get("link") or ""
    mt = re.search(r"xsec_token=([^&]+)", link)
    if mt:
        tok = mt.group(1)
    notes[inner["id"]] = {"note_id": inner["id"], "xsec_token": tok,
                          "xsec_source": "app_share", "title": inner.get("title") or ""}

with_token = {k: v for k, v in notes.items() if v["xsec_token"]}
print(f"带token笔记卡片: {len(with_token)}")

# 与现有 note_list.json 对比
old = {n["note_id"] for n in json.loads((BASE / "note_list.json").read_text(encoding="utf-8"))}
new = {k: v for k, v in with_token.items() if k not in old}
print(f"新增: {len(new)}")
for k, v in new.items():
    print(f"  + {k} 《{v['title'][:32]}》")

if new:
    (BASE / "note_list_new.json").write_text(
        json.dumps(list(new.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print("-> note_list_new.json 已保存，待并入")
