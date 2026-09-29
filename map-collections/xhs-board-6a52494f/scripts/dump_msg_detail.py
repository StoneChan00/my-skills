# -*- coding: utf-8 -*-
"""查看 ct=3 / ct=10 消息的完整结构，确定笔记链接格式。"""
import json
from pathlib import Path

p = Path(r"D:\2_Projects\github\StoneChan00\my-skills\chat-history-p1.json")
raw = p.read_text(encoding="utf-8")
j = json.loads(raw[raw.find("{"):])
msgs = j["data"]["out_message_list"]

for m in msgs:
    try:
        c = json.loads(m["content"])
    except Exception:
        continue
    ct = c.get("content_type")
    if m["store_id"] in (81, 76, 75, 74) and ct in (3, 10):
        print(f"===== store_id={m['store_id']} ct={ct} =====")
        print(json.dumps(c, ensure_ascii=False, indent=1)[:1200])
        print()
