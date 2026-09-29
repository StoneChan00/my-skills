# -*- coding: utf-8 -*-
"""分析全量聊天消息：找越南专辑相关的笔记添加事件和笔记卡片。"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

p = Path(r"D:\2_Projects\github\StoneChan00\my-skills\map-collections\xhs-board-6a52494f\chat-messages-clean.json")
raw = p.read_text(encoding="utf-8")
msgs = json.loads(raw)
print(f"total: {len(msgs)}")

CST = timezone(timedelta(hours=8))
note_cards = {}       # note_id -> title (ct=3, type=note)
board_adds = []       # ct=10 events
shared_boards = []    # ct=3 type=sharedBoard/album

for m in msgs:
    at = datetime.fromtimestamp(m["at"] / 1000, tz=CST).strftime("%m-%d %H:%M")
    if m["ct"] == 3 and m["type"] == "note" and m["id"]:
        note_cards[m["id"]] = m["title"]
    if m["ct"] == 10 and m["biz"] == "board_add_note_passive":
        board_adds.append((m["sid"], at, m["rl"]))
    if m["ct"] == 3 and m["type"] in ("sharedBoard", "") and ("board/" in m["link"] or "shared_board" in m["link"]):
        shared_boards.append((m["sid"], at, m["title"], m["link"]))

print(f"\n=== 笔记卡片 (ct=3 type=note): {len(note_cards)} 个不同笔记 ===")
for nid, t in note_cards.items():
    print(f"  {nid}  《{t[:40]}》")

print(f"\n=== 专辑添加事件 (ct=10): {len(board_adds)} 条 ===")
boards = {}
for sid, at, rl in board_adds:
    for r in rl.split("|") if rl else []:
        name, link = r.split(":", 1) if ":" in r else (r, "")
        boards.setdefault((name, link), []).append(at)
for (name, link), times in boards.items():
    print(f"  专辑《{name}》 {link}  添加事件 {len(times)} 次, 时间范围 {times[0]} ~ {times[-1]}")

print(f"\n=== 共享专辑邀请/分享: {len(shared_boards)} ===")
for sid, at, title, link in shared_boards:
    print(f"  [{at}] {title} {link}")

# 时间线概览
print("\n=== 关键时间线 ===")
for m in msgs:
    at = datetime.fromtimestamp(m["at"] / 1000, tz=CST).strftime("%m-%d %H:%M")
    tag = ""
    if m["ct"] == 10:
        tag = "ADD:" + m["rl"][:60]
    elif m["ct"] == 3 and m["type"] == "note":
        tag = f"NOTE {m['id'][:8]} 《{m['title'][:30]}》"
    elif m["ct"] == 3:
        tag = f"CARD {m['type']} 《{m['title']}》 {m['link'][:60]}"
    elif m["ct"] == 1:
        pass
    if tag:
        print(f"  {at} #{m['sid']:>3} {tag}")
