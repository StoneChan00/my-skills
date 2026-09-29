# -*- coding: utf-8 -*-
"""解析 JoJo 聊天记录，找分享的笔记链接。"""
import json
import sys
from pathlib import Path

p = Path(r"D:\2_Projects\github\StoneChan00\my-skills\chat-history-p1.json")
raw = p.read_text(encoding="utf-8")
j = json.loads(raw[raw.find("{"):])
msgs = j["data"]["out_message_list"]
print(f"messages: {len(msgs)}")

for m in msgs:
    try:
        c = json.loads(m["content"])
    except Exception:
        c = {"raw": str(m["content"])[:100]}
    sender = "stone" if m["sender_id"].startswith("5b58") else "JoJo"
    ct = c.get("content_type")
    body = str(c.get("content") or c.get("front_chain") or "")[:70]
    extra_keys = [k for k in c.keys() if k not in
                  ("content", "content_type", "not_front_chain", "not_unread_count", "front_chain")]
    extras = {k: c[k] for k in extra_keys}
    print(f"{m['store_id']:>4} {sender:5s} ct={ct} | {body} | {json.dumps(extras, ensure_ascii=False)[:180] if extras else ''}")
