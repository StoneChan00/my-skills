# -*- coding: utf-8 -*-
"""抖音新地点: 定位(Photon) + 合并进 osm_geocoded_final.json。"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FINAL = BASE / "osm_geocoded_final.json"
UA = "my-skills-map-collection-builder/1.0"
VN_BBOX = "102,8,110.5,23.5"
CITY_BIAS = {"胡志明市": (10.776, 106.700)}

# 抖音提取的新地点（display/query/city/category/notes/douyin源）
NEW = [
    {"display": "Phở Hưng 阿雄牛肉粉（四大天王）", "query": "Pho Hung Ho Chi Minh", "city": "胡志明市", "category": "美食",
     "source": "douyin", "notes": ["抖音·湾区B哥《牛肉粉四大天王》"], "meta": "汤浓牛肉嫩 6点-凌晨1点"},
    {"display": "Phở Lẽ 锦利牛肉粉（四大天王）", "query": "Pho Le Ho Chi Minh", "city": "胡志明市", "category": "美食",
     "source": "douyin", "notes": ["抖音·湾区B哥《牛肉粉四大天王》"], "meta": "当地家庭常去 汤头厚"},
    {"display": "阿琼牛肉炖粉（范五老街附近）", "query": "Bui Vien Street", "city": "胡志明市", "category": "美食",
     "source": "douyin", "approx": True, "notes": ["抖音·湾区B哥《牛肉粉四大天王》"], "meta": "牛肉炖粉 6点-午夜"},
    {"display": "Bún Mọc Thanh Mai（清汤粉）", "query": "Bun Moc Thanh Mai Ho Chi Minh", "city": "胡志明市", "category": "美食",
     "source": "douyin", "notes": ["抖音·曾yaya《胡志明美食合集》"], "meta": "骨头熬清汤 像家里煮的"},
    {"display": "Cò Tú Cà Mau（越南海鲜）", "query": "Co Tu Ca Mau Ho Chi Minh", "city": "胡志明市", "category": "美食",
     "source": "douyin", "notes": ["抖音·曾yaya《胡志明美食合集》"], "meta": "香草炖贝壳 炒虾 芒果沙拉"},
    {"display": "Sầu Riêng Nguyên Ký 榴莲一条街", "query": "Sau Rieng Nguyen Ky Ho Chi Minh", "city": "胡志明市", "category": "购物",
     "source": "douyin", "notes": ["抖音·曾yaya《胡志明美食合集》"], "meta": "猫山王约40rmb/kg"},
    {"display": "Five Boys 鲜果沙冰（小巷）", "query": "Five Boys Saigon smoothie", "city": "胡志明市", "category": "美食",
     "source": "douyin", "notes": ["抖音·曾yaya《胡志明美食合集》"], "meta": "只有水果和冰不加糖"},
    {"display": "Breadventure 法棍（周五六日营业）", "query": "Breadventure 24 Do Quang Ho Chi Minh", "city": "胡志明市", "category": "美食",
     "source": "douyin", "address": "24 Đ. Đỗ Quang, An Khánh", "notes": ["抖音·十一Eleven《为了这口法棍排45分钟》"], "meta": "早8点排队45分钟 黄油果酱法棍"},
    {"display": "爆火膏蟹餐厅（黄油蟹/罗氏虾）", "query": "Ben Thanh Market", "city": "胡志明市", "category": "美食",
     "source": "douyin+xhs", "approx": True, "notes": ["抖音·十一Eleven《螃蟹店排队》", "小红书《本来以为踩雷》"], "meta": "蒜香黄油/酸角炒蟹 一百一只 饭点排队"},
]

APPROX_FALLBACK = {
    "阿琼牛肉炖粉（范五老街附近）": ("范五老街附近", 10.76775, 106.69248),
    "爆火膏蟹餐厅（黄油蟹/罗氏虾）": ("第一郡（具体位置见视频）", 10.77200, 106.69800),
    "Five Boys 鲜果沙冰（小巷）": ("D1小巷", 10.77500, 106.70000),
    "Sầu Riêng Nguyên Ký 榴莲一条街": ("榴莲街", 10.77000, 106.69500),
}


def photon(q, city):
    blat, blon = CITY_BIAS.get(city, (10.776, 106.700))
    params = {"q": q, "limit": "3", "bbox": VN_BBOX, "lat": str(blat), "lon": str(blon)}
    url = "https://photon.komoot.io/api/?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            j = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []
    return [{"lat": f["geometry"]["coordinates"][1], "lon": f["geometry"]["coordinates"][0],
             "name": f["properties"].get("name") or ""} for f in j.get("features", [])]


def main():
    data = json.loads(FINAL.read_text(encoding="utf-8"))
    existing = {d["display"] for d in data}
    added = 0
    for loc in NEW:
        if loc["display"] in existing:
            continue
        results = photon(loc["query"], loc["city"])
        pick = results[0] if results else None
        # 城市合理性
        if pick and not (10.5 < pick["lat"] < 11.05 and 106.35 < pick["lon"] < 107.05):
            pick = None
        if pick:
            entry = {"status": "ok", "lat": pick["lat"], "lon": pick["lon"], "precision": "photon",
                     "osm_name": pick["name"], "approx": bool(loc.get("approx")), **loc}
        elif loc["display"] in APPROX_FALLBACK:
            hint, lat, lon = APPROX_FALLBACK[loc["display"]]
            entry = {"status": "ok", "lat": lat, "lon": lon, "precision": "approx",
                     "osm_name": hint, "approx": True, **loc}
        else:
            entry = {"status": "ok", "lat": 10.775, "lon": 106.700, "precision": "approx",
                     "osm_name": "D1中心", "approx": True, **loc}
        data.append(entry)
        added += 1
        mark = "" if entry["precision"] == "photon" else " ⚠approx"
        print(f"  + {entry['display'][:30]:32s} -> {entry['lat']:.5f},{entry['lon']:.5f}{mark}")
        time.sleep(0.4)

    # 更新已有的牛蛙粥条目（跨平台验证 + 补充信息）
    for d in data:
        if "牛蛙粥" in d["display"]:
            d["notes"] = d.get("notes", []) + ["抖音·十一Eleven《粉红教堂旁田鸡粥》(18:30营业)"]
            d["douyin_verified"] = True
            print(f"  ~ 更新: {d['display']} (+抖音交叉验证)")

    FINAL.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(1 for d in data if d.get("status") == "ok")
    print(f"\n合并完成: 新增 {added}, 总点位 {total}")


if __name__ == "__main__":
    main()
