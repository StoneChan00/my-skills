# -*- coding: utf-8 -*-
"""用搜索到的权威地址重定位 5 个误配点位。"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FINAL = BASE / "osm_geocoded_final.json"
UA = "my-skills-map-collection-builder/1.0"
VN_BBOX = "102,8,110.5,23.5"

FIXES = {
    "Phở Hưng 阿雄牛肉粉（四大天王）": {
        "query": "241 Nguyen Trai Ho Chi Minh",
        "address": "241-243 Nguyễn Trãi, Nguyễn Cư Trinh, Quận 1（米其林推荐）",
        "osm_name_hint": "Phở Hưng",
    },
    "Phở Lẽ 锦利牛肉粉（四大天王）": {
        "query": "413 Nguyen Trai Ho Chi Minh",
        "address": "413-415 Nguyễn Trãi, Q5（米其林,老店）/ 分店 303-305 Võ Văn Tần, Q3",
        "osm_name_hint": "Phở Lẽ",
    },
    "Cò Tú Cà Mau（越南海鲜）": {
        "query": "219 Hoang Sa Ho Chi Minh",
        "address": "219 Hoàng Sa, Tân Định, Quận 1",
        "osm_name_hint": "Cô Tư Cà Mau",
    },
    "Bún Mọc Thanh Mai（清汤粉）": {
        "query": "14 Truong Dinh Ho Chi Minh",
        "address": "14 Trương Định, Bến Thành, Quận 1（滨城市场西侧）",
        "osm_name_hint": "Bún Mọc Thanh Mai",
    },
    "Sầu Riêng Nguyên Ký 榴莲一条街": {
        "query": "Nguyen Ky street Ho Chi Minh",
        "address": "Nguyễn Ký 街（榴莲店聚集）",
        "osm_name_hint": "榴莲一条街",
    },
}


def photon(q):
    params = {"q": q, "limit": "3", "bbox": VN_BBOX, "lat": "10.776", "lon": "106.700"}
    url = "https://photon.komoot.io/api/?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            j = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []
    return [{"lat": f["geometry"]["coordinates"][1], "lon": f["geometry"]["coordinates"][0],
             "name": f["properties"].get("name") or "",
             "disp": (f["properties"].get("street") or "") + " " + (f["properties"].get("city") or "")}
            for f in j.get("features", [])]


def main():
    data = json.loads(FINAL.read_text(encoding="utf-8"))
    for d in data:
        if d["display"] in FIXES:
            fx = FIXES[d["display"]]
            res = photon(fx["query"])
            pick = res[0] if res and 10.4 < res[0]["lat"] < 11.0 and 106.3 < res[0]["lon"] < 107.0 else None
            if pick:
                d.update({"lat": pick["lat"], "lon": pick["lon"], "precision": "photon-addr",
                          "osm_name": fx["osm_name_hint"], "approx": False})
                print(f"  ✓ {d['display'][:28]:30s} -> {pick['lat']:.5f},{pick['lon']:.5f} ({pick['disp'][:30]})")
            else:
                d.update({"osm_name": fx["osm_name_hint"], "approx": True, "precision": "approx"})
                print(f"  ⚠ {d['display'][:28]:30s} -> 地址搜索未中, 保持近似")
            d["address"] = fx["address"]
            time.sleep(0.4)

    FINAL.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for d in data if d.get("status") == "ok")
    print(f"\n完成, 总点位 {ok}")


if __name__ == "__main__":
    main()
