# -*- coding: utf-8 -*-
"""分析新增的聊天消息（store>83）：越南笔记分享。"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

raw = Path(r"D:\2_Projects\github\StoneChan00\my-skills\chat-new-messages.json").read_text(encoding="utf-8")
j = json.loads(raw)
if isinstance(j, str):
    j = json.loads(j)
CST = timezone(timedelta(hours=8))

print(f"新消息: {len(j)} 条\n")
note_ids, xhslinks = {}, []
for m in j:
    at = datetime.fromtimestamp(m["at"] / 1000, tz=CST).strftime("%H:%M:%S")
    who = m["from"]
    kind = {0: "系统", 1: "文本", 2: "图片", 3: "卡片", 10: "通知"}.get(m["ct"], str(m["ct"]))
    t = m["title"] or (m["text"] or "")[:60]
    extra = ""
    if m["type"] == "note" and m["nid"]:
        note_ids[m["nid"]] = m["title"]
        extra = f" NOTE={m['nid'][:10]}"
    # 文本消息里找 xhslink
    txt = (m["text"] or "")
    if "xhslink" in txt:
        import re
        for u in re.findall(r"https://xhslink\.cn/\S+", txt):
            xhslinks.append(u.split("先复制")[0].strip())
            extra += " XHSLINK"
    print(f"  {at} {who:5s} {kind} | {t[:60]}{extra}")

print(f"\n=== 笔记卡片(带ID): {len(note_ids)} ===")
print(f"=== 文本中的xhslink: {len(xhslinks)} ===")
for u in xhslinks[:5]:
    print("  ", u)

Path(r"D:\2_Projects\github\StoneChan00\my-skills\map-collections\xhs-board-6a52494f\chat-vietnam-notes.json").write_text(
    json.dumps({"note_cards": note_ids, "xhslinks": xhslinks}, ensure_ascii=False, indent=1), encoding="utf-8")
print("\nsaved -> chat-vietnam-notes.json")
