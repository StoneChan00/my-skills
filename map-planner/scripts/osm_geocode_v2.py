# -*- coding: utf-8 -*-
"""
海外地点定位 v2: Photon(komoot, 可直连) 为主 + Nominatim(走本地代理) 兜底。
结果: osm_geocoded.json (增量, 每条落盘)
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import _common
BASE = _common.base_from_argv()  # --dir <collection目录> 可指定，缺省取最新
LOC_FILE = BASE / "locations.json"
OUT_FILE = BASE / "osm_geocoded.json"

CITY_BIAS = {
    "胡志明市": ("Ho Chi Minh City", 10.776, 106.700),
    "芽庄": ("Nha Trang", 12.239, 109.196),
    "岘港": ("Da Nang", 16.054, 108.202),
}
VN_BBOX = "102,8,110.5,23.5"
PROXY = "http://127.0.0.1:7897"
UA = "my-skills-map-collection-builder/1.0"


def http_get(url: str, use_proxy: bool = False, timeout: int = 15) -> str:
    handlers = []
    if use_proxy:
        handlers.append(urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}))
    opener = urllib.request.build_opener(*handlers) if handlers else urllib.request.build_opener()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with opener.open(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def photon_search(q: str, city: str):
    _, blat, blon = CITY_BIAS.get(city, ("", 10.8, 106.7))
    params = {"q": q, "limit": "3", "bbox": VN_BBOX, "lat": str(blat), "lon": str(blon)}
    url = "https://photon.komoot.io/api/?" + urllib.parse.urlencode(params)
    try:
        j = json.loads(http_get(url))
    except Exception as e:
        print(f"    [P-ERR] {str(e)[:60]}", flush=True)
        return []
    out = []
    for f in j.get("features", []):
        p = f.get("properties", {})
        c = f.get("geometry", {}).get("coordinates", [None, None])
        out.append({
            "lon": c[0], "lat": c[1],
            "name": p.get("name") or "",
            "city": p.get("city") or p.get("county") or "",
            "state": p.get("state") or "",
            "country": p.get("country") or "",
            "osm_key": p.get("osm_key") or "",
        })
    return out


def nominatim_search(q: str):
    params = {"q": q, "format": "jsonv2", "limit": "3", "countrycodes": "vn",
              "accept-language": "vi,en"}
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    try:
        j = json.loads(http_get(url, use_proxy=True))
    except Exception as e:
        print(f"    [N-ERR] {str(e)[:60]}", flush=True)
        return []
    return [{"lon": float(r["lon"]), "lat": float(r["lat"]), "name": r.get("name", ""),
             "city": (r.get("display_name") or "")} for r in j]


def city_matches(res: dict, city: str) -> bool:
    en_city = CITY_BIAS.get(city, ("",))[0]
    hay = f"{res.get('city','')} {res.get('state','')} {res.get('country','')}".lower()
    names = {"胡志明市": ["ho chi minh", "sai gon", "saigon"], "芽庄": ["nha trang", "khánh hòa", "khanh hoa"],
             "岘港": ["da nang", "đà nẵng", "danang"]}
    return any(k in hay for k in names.get(city, [en_city.lower()]))


def geocode_one(loc: dict):
    city = loc["city"]
    queries = [loc["query"]]
    if loc.get("fallback_query"):
        queries.append(loc["fallback_query"])
    for qi, q in enumerate(queries):
        results = photon_search(q, city)
        # 优先取城市匹配的结果
        pick = next((r for r in results if city_matches(r, city)), None) or (results[0] if results else None)
        if pick and pick["lat"] is not None:
            return {"status": "ok", "engine": "photon", "via": q,
                    "lat": pick["lat"], "lon": pick["lon"],
                    "osm_name": pick["name"], "osm_city": pick.get("city", ""),
                    "city_ok": city_matches(pick, city),
                    "approx": bool(loc.get("approx")) or qi > 0,
                    **loc}
    # Nominatim 兜底（走代理）
    for q in queries:
        results = nominatim_search(f"{q}, {CITY_BIAS.get(city, ('',))[0]}")
        if results:
            r = results[0]
            return {"status": "ok", "engine": "nominatim", "via": q,
                    "lat": r["lat"], "lon": r["lon"],
                    "osm_name": r["name"], "osm_city": r["city"][:60],
                    "city_ok": True, "approx": bool(loc.get("approx")),
                    **loc}
    return {"status": "no_match", **loc}


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
            mark = " ~" if r.get("approx") else ("" if r.get("city_ok") else " ?城市")
            print(f"  [{i}/{len(locations)}][OK{mark}] {loc['display'][:26]:28s} -> {r['lat']:.5f},{r['lon']:.5f} {r['osm_name'][:22]}", flush=True)
        else:
            miss += 1
            print(f"  [{i}/{len(locations)}][MISS] {loc['display'][:40]}", flush=True)
        OUT_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(0.35)

    print(f"\n完成: ok={ok} miss={miss} cached={cached} / {len(locations)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
