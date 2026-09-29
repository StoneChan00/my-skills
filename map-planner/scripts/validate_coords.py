# -*- coding: utf-8 -*-
"""校验：每个点位坐标是否落在其声明城市的合理范围内。"""
import json
from pathlib import Path

import _common
BASE = _common.base_from_argv()
d = json.loads((BASE / "osm_geocoded_final.json").read_text(encoding="utf-8"))

RANGES = {
    "胡志明市": (10.5, 11.05, 106.35, 107.05),
    "芽庄": (11.9, 12.55, 108.95, 109.45),
    "岘港": (15.85, 16.25, 108.0, 108.4),
}
bad = 0
for x in d:
    if x.get("status") != "ok":
        continue
    lat, lon = x["lat"], x["lon"]
    lo1, hi1, lo2, hi2 = RANGES.get(x["city"], (0, 99, 0, 99))
    if not (lo1 < lat < hi1 and lo2 < lon < hi2):
        bad += 1
        print(f"  [异常] {x['display']} ({x['city']}) -> {lat:.4f},{lon:.4f} [{x.get('precision')}]")
print(f"校验完成: {bad} 个城市异常" if bad else "校验完成: 全部坐标落在对应城市范围内 ✓")
