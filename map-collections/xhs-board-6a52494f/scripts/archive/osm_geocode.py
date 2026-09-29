# -*- coding: utf-8 -*-
"""
OSM/Nominatim 海外地点定位（越南）。
海外无 GCJ-02 偏移，WGS-84 坐标可直接用于高德地图小程序导入。

用法: python osm_geocode.py          # 增量执行，结果存 osm_geocoded.json
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LOC_FILE = BASE / "locations.json"
OUT_FILE = BASE / "osm_geocoded.json"

CITY_EN = {"胡志明市": "Ho Chi Minh City", "芽庄": "Nha Trang", "岘港": "Da Nang"}
UA = "my-skills-map-collection-builder/1.0 (travel planning; contact: local script)"
SLEEP_S = 1.1  # Nominatim 政策: 最大 1 req/s


def nominatim_search(q: str, limit: int = 3):
    params = {
        "q": q, "format": "jsonv2", "limit": str(limit),
        "countrycodes": "vn", "accept-language": "vi,en,zh",
    }
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"    [ERR] {e}")
        return []


def geocode_one(loc: dict):
    city_en = CITY_EN.get(loc["city"], loc["city"])
    # 主查询: query + 城市
    results = nominatim_search(f"{loc['query']}, {city_en}")
    # 兜底: query 本身
    if not results:
        results = nominatim_search(loc["query"])
    # 兜底2: fallback_query + 城市
    if not results and loc.get("fallback_query"):
        results = nominatim_search(f"{loc['fallback_query']}, {city_en}")
    if not results:
        return {"status": "no_match", **loc}

    best = results[0]
    return {
        "status": "ok",
        "lat": float(best["lat"]),
        "lon": float(best["lon"]),
        "osm_name": best.get("name") or "",
        "osm_display": best.get("display_name", "")[:150],
        "osm_type": best.get("type") or "",
        "approx": bool(loc.get("approx")) or bool(loc.get("fallback_query") and not any(
            w in (best.get("display_name") or "").lower() for w in loc["query"].lower().split()[:2])),
        **loc,
    }


def main():
    locations = json.loads(LOC_FILE.read_text(encoding="utf-8"))
    done = {}
    if OUT_FILE.exists():
        for it in json.loads(OUT_FILE.read_text(encoding="utf-8")):
            if it.get("status") == "ok":
                done[it["display"]] = it

    out, ok, miss, cached = [], 0, 0, 0
    for i, loc in enumerate(locations, 1):
        if loc["display"] in done:
            out.append(done[loc["display"]])
            cached += 1
            continue
        r = geocode_one(loc)
        out.append(r)
        if r["status"] == "ok":
            ok += 1
            mark = " ~" if r.get("approx") else ""
            print(f"  [{i}/{len(locations)}][OK{mark}] {loc['display'][:28]:30s} -> {r['lat']:.5f},{r['lon']:.5f} {r['osm_name'][:24]}", flush=True)
        else:
            miss += 1
            print(f"  [{i}/{len(locations)}][MISS] {loc['display'][:40]}", flush=True)
        # 每条即时落盘（断点安全）
        OUT_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(SLEEP_S)

    print(f"\n完成: ok={ok} miss={miss} cached={cached} / {len(locations)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
