# -*- coding: utf-8 -*-
"""测试高德海外 POI 搜索 API 对越南地点的覆盖。"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

CONFIG = Path(r"D:\2_Projects\github\StoneChan00\my-skills\.opencode\skills\travel-planner\config.json")
KEY = json.loads(CONFIG.read_text(encoding="utf-8"))["amap_key"]


def try_api(path, params, label):
    params = {**params, "key": KEY}
    url = f"https://restapi.amap.com{path}?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            j = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[{label}] 请求异常: {e}")
        return
    if j.get("status") != "1":
        print(f"[{label}] status={j.get('status')} infocode={j.get('infocode')} {j.get('info')}")
        return
    pois = j.get("pois") or []
    print(f"[{label}] 命中 {len(pois)} 个 POI")
    for p in pois[:3]:
        print(f"    {p.get('name')} | {p.get('cityname') or p.get('pname') or ''} | {p.get('address', '')[:40]} | {p.get('location')}")


# 海外搜索 v3
try_api("/v3/place/overseas/text", {"keywords": "新山一机场", "city": "胡志明市"}, "overseas/text 新山一机场")
try_api("/v3/place/overseas/text", {"keywords": "胡志明", "city": "胡志明市"}, "overseas/text 胡志明")
# geocode 海外
try_api("/v3/geocode/geo", {"address": "胡志明市新山一国际机场"}, "geocode 新山一机场")
# v5 搜索
try_api("/v5/place/text", {"keywords": "新山一机场"}, "v5/text 新山一机场")
