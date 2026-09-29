# -*- coding: utf-8 -*-
"""整理 vietnam-note-list.json → note_list.json（read_notes.py 的输入格式）。"""
import json
from pathlib import Path

BASE = Path(r"D:\2_Projects\github\StoneChan00\my-skills\map-collections\xhs-board-6a52494f")
raw = (Path(r"D:\2_Projects\github\StoneChan00\my-skills\vietnam-note-list.json")).read_text(encoding="utf-8")
j = json.loads(raw)
if isinstance(j, str):
    j = json.loads(j)

notes = [n for n in j if n.get("xsec_token")]
print(f"带 token 笔记: {len(notes)}")
(BASE / "note_list.json").write_text(json.dumps(notes, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"saved -> {BASE / 'note_list.json'}")
for n in notes[:5]:
    print(f"  {n['note_id']} 《{n['title'][:30]}》 tok={n['xsec_token'][:20]}...")
