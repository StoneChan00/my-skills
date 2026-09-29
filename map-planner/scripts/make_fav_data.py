# -*- coding: utf-8 -*-
"""生成高德个人收藏批量导入数据文件（91 点 + 待删测试项）。"""
import json
from pathlib import Path

import _common
BASE = _common.base_from_argv()  # --dir <collection目录> 可指定，缺省取最新
FINAL = BASE / "osm_geocoded_final.json"
OUT = BASE / "amap_fav_data.json"

data = [d for d in json.loads(FINAL.read_text(encoding="utf-8")) if d.get("status") == "ok"]

items = []
for d in data:
    addr = f"越南·{d['city']}" + (f"·{d['address']}" if d.get("address") else "")
    comment = " | ".join(f"《{n}》" for n in d.get("notes", [])[:2])
    meta = d.get("meta") or ""
    if d.get("source"):
        comment = ("抖音" if "douyin" in d["source"] else "小红书") + ("·" if comment else "") + comment
    if meta:
        comment = (comment + " | " if comment else "") + meta
    if d.get("approx"):
        comment = (comment + " | " if comment else "") + "⚠位置近似"
    items.append({
        "name": d["display"][:40],
        "lon": round(float(d["lon"]), 6),
        "lat": round(float(d["lat"]), 6),
        "addr": addr[:80],
        "comment": comment[:120],
    })

payload = {
    "delete_item_id": "07b6ec739fffed6ecee5e70c782b4eda",  # 捕获时误收藏的新乐路东正教堂
    "ver": "aroxxAAAAAABAAAB",  # 最新已知同步版本号
    "items": items,
}
OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
print(f"数据文件: {OUT} ({len(items)} 点位)")
for it in items[:3]:
    print(f"  {it['name']} | {it['lon']},{it['lat']} | {it['addr']}")
