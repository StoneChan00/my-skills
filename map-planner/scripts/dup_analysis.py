# -*- coding: utf-8 -*-
"""分析 91 个点的重复情况：完全同名 / 完全同坐标 / 坐标堆叠（近似挂靠导致）。"""
import json
from collections import Counter, defaultdict
from pathlib import Path

import _common
BASE = _common.base_from_argv()
d = [x for x in json.loads((BASE / "osm_geocoded_final.json").read_text(encoding="utf-8")) if x.get("status") == "ok"]

print(f"总数: {len(d)}")

# 1. 同名重复
names = Counter(x["display"] for x in d)
dup_names = {k: v for k, v in names.items() if v > 1}
print(f"\n完全同名重复: {len(dup_names)}")
for k, v in dup_names.items():
    print(f"  {v}x {k}")

# 2. 同坐标堆叠
by_coord = defaultdict(list)
for x in d:
    by_coord[(round(x["lat"], 5), round(x["lon"], 5))].append(x)
stacks = {k: v for k, v in by_coord.items() if len(v) > 1}
print(f"\n坐标完全相同(堆叠): {len(stacks)} 组, 涉及 {sum(len(v) for v in stacks.values())} 个点")
for (lat, lon), group in sorted(stacks.items(), key=lambda kv: -len(kv[1])):
    approx_marks = "⚠近似" if all(g.get("approx") for g in group) else ("混合" if any(g.get("approx") for g in group) else "精确")
    print(f"\n  [{len(group)}个 @ {lat},{lon} {approx_marks}]")
    for g in group:
        print(f"    - {g['display']}{' ⚠' if g.get('approx') else ''}")

# 3. 近距离聚类（<200m）
print("\n--- 200m 内聚类（不含上组完全同点）---")
import math
def dist(a, b):
    return math.hypot((a["lat"] - b["lat"]) * 111000, (a["lon"] - b["lon"]) * 111000 * math.cos(math.radians(a["lat"])))
seen = set()
for i, a in enumerate(d):
    for j in range(i + 1, len(d)):
        b = d[j]
        if dist(a, b) < 200:
            key = tuple(sorted([a["display"], b["display"]]))
            if key not in seen:
                seen.add(key)
                print(f"  {dist(a, b):.0f}m: {a['display'][:22]} <-> {b['display'][:22]}")
print(f"\n200m 内不同点对: {len(seen)} 对")
