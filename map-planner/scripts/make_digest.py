# -*- coding: utf-8 -*-
"""把 notes/*.json 压缩成紧凑摘要（标题+正文+话题+位置字段），供地点提取。"""
import json
import re
from pathlib import Path

import _common
BASE = _common.base_from_argv()  # --dir <collection目录> 可指定，缺省取最新
NOTES = BASE / "notes"

def clean(text: str) -> str:
    text = re.sub(r"\[[^\]]{1,8}?[Rr]\]", " ", text)      # [emoji R]
    text = re.sub(r"\[话题\]", "", text)
    text = re.sub(r"#([^#\n]{1,30})#", r" #\1 ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

out = []
for f in sorted(NOTES.glob("*.json")):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        continue
    title = clean(str(d.get("title") or ""))
    desc = clean(str(d.get("desc") or ""))[:800]
    tags = " ".join(t for t in re.findall(r"#(\S+)", str(d.get("desc") or "")) if len(t) < 25)[:120]
    ip = str(d.get("ip_location") or "")
    out.append({"id": d.get("note_id") or f.stem, "title": title, "desc": desc, "tags": tags, "ip": ip})

out.sort(key=lambda x: x["title"])
(BASE / "notes_digest.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"摘要: {len(out)} 篇 -> notes_digest.json ({(BASE / 'notes_digest.json').stat().st_size} bytes)")
