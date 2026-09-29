# -*- coding: utf-8 -*-
"""
定位修复 pass:
- KNOW: 高置信度知识坐标（著名地标）
- RETRY: 备选查询（更简洁的 Photon 查询词）
- APPROX: 近似定位（挂靠地标，描述列注明）
- 其余仍无法定位 → needs_manual 列表
输出: osm_geocoded_final.json
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
IN_FILE = BASE / "osm_geocoded.json"
OUT_FILE = BASE / "osm_geocoded_final.json"
UA = "my-skills-map-collection-builder/1.0"
VN_BBOX = "102,8,110.5,23.5"

# 高置信知识坐标 (WGS84) —— 著名地标
KNOW = {
    "圣母大教堂（红教堂，维修中）": (10.77978, 106.69904),
    "Landmark 81": (10.79488, 106.72185),
    "Blank Lounge（Landmark 81 75-76F）": (10.79488, 106.72185),
    "Cong Café 粉红教堂店（椰子绿米冰沙）": (10.78872, 106.69127),
}

# 备选 Photon 查询（更短/越南语原生名/含地址）
RETRY = {
    "Man Moi（战争纪念馆附近）": ["Man Moi", "Mạnh Mới restaurant"],
    "Linh 咖啡（盐咖啡）": ["Linh coffee", "Linh Cafe"],
    "Lvoire Pastry（第一甜品店）": ["Lvoire"],
    "Nhà Tú（蟹黄牡蛎肥牛火锅）": ["Nha Tu", "Nhà Tú"],
    "Pho Hoa Pasteur": ["Pho Hoa Pasteur 245", "Phở Hòa Pasteur"],
    "Bếp Cuốn Sài Gòn（米其林越南菜）": ["Bep Cuon", "Bếp Cuốn"],
    "Ngọc Thạch Quán（甜品）": ["Ngoc Thach", "Ngọc Thạch"],
    "7 Bridges Brewing Co（西贡精酿）": ["7 Bridges"],
    "Stir（Best 50）": ["Stir Saigon"],
    "RAW + Atelier（Best 50 鸡尾酒）": ["RAW Atelier", "Atelier Saigon"],
    "Summer Experiment（Best 50）": ["Summer Experiment"],
    "Tamarind Hidden Cocktail Bar": ["Tamarind cocktail Saigon"],
    "SIZ SPA": ["154 Cong Quynh", "SIZ Spa"],
    "Sa Spa（1区）": ["Sa Spa Quan 1"],
    "Sả Spa Central": ["Sa Spa Central"],
    "Phaya Thai Spa Quận 1": ["Phaya Thai"],
    "Sen Trắng Spa & Wellness": ["Sen Trang"],
    "Xíu Spa": ["Xiu Spa"],
    "KIM HEALTH & BEAUTY Spa": ["Kim Health Beauty"],
    "An's Spa & Massage（五星强推）": ["Ans spa", "An's spa"],
    "Temple Leaf（按摩）": ["Temple Leaf"],
    "BINGDOU Bingsu（牛油果冰淇淋）": ["Bingdou"],
    "Kem Bơ Vfruit（牛油果冰淇淋）": ["Vfruit", "Kem bo Vfruit"],
    "BÁNH CANH GHẸ CÔ BA MIỀN BIỂN（皮皮虾粗粉）": ["Banh Canh Ghe", "Bánh canh ghẹ"],
    "Luxury Anna Spa（芽庄按摩）": ["172 Bach Dang Nha Trang", "Luxury Anna"],
    "Ăn Thôi 2（米其林必比登越南菜）": ["An Thoi Nha Trang", "64C Nguyen Thi Minh Khai"],
    "Pizza 4P's": ["Pizza 4Ps"],
    "La Viet Coffee（亚洲第六咖啡店）": ["La Viet Coffee"],
    "Hải Sản Thảo Tiến（机场顺路海鲜）": ["Thao Tien", "Hai San Thao Tien"],
    "Mia 度假酒店（独栋院子+独立沙滩）": ["Mia Resort"],
    "Tyro Seafood Restaurant": ["Tyro seafood"],
    "Ot Hiem（越南菜）": ["Ot Hiem", "Ốt Hiếm"],
    "Mộc Quán Seafood（海鲜大排档）": ["Moc Quan"],
    "Quán ăn X.O（本地苍蝇馆子）": ["Quan An XO"],
    "96 中国超市（旁旅行社换汇汇率3870）": ["China Market Nha Trang", "96 market Nha Trang"],
}

# 近似挂靠（重试失败后用：备注里的空间关系）
APPROX = {
    "Man Moi（战争纪念馆附近）": ("战争遗迹博物馆旁", 10.77936, 106.69228),
    "Linh 咖啡（盐咖啡）": ("Phở Việt Nam 隔壁", 10.77125, 106.69621),
    "Lvoire Pastry（第一甜品店）": ("柏悦酒店附近(D1)", 10.77890, 106.70050),
    "Nhà Tú（蟹黄牡蛎肥牛火锅）": ("D1 中心区", 10.77700, 106.70000),
    "Pho Hoa Pasteur": ("Pasteur 街", 10.78020, 106.69220),
    "Bếp Cuốn Sài Gòn（米其林越南菜）": ("D1 中心区", 10.77700, 106.70000),
    "Ngọc Thạch Quán（甜品）": ("D1 中心区", 10.77700, 106.70000),
    "7 Bridges Brewing Co（西贡精酿）": ("一区", 10.77500, 106.70100),
    "Stir（Best 50）": ("D1 酒吧区", 10.77600, 106.70340),
    "RAW + Atelier（Best 50 鸡尾酒）": ("D1 酒吧区", 10.77600, 106.70340),
    "Summer Experiment（Best 50）": ("D1 酒吧区", 10.77600, 106.70340),
    "Tamarind Hidden Cocktail Bar": ("D1 酒吧区", 10.77600, 106.70340),
    "Sả Spa Central": ("D1", 10.78424, 106.69408),
    "Phaya Thai Spa Quận 1": ("D1", 10.78012, 106.70386),
    "Sen Trắng Spa & Wellness": ("D1", 10.78386, 106.69822),
    "Xíu Spa": ("D1", 10.77500, 106.70000),
    "KIM HEALTH & BEAUTY Spa": ("D1", 10.77500, 106.70000),
    "An's Spa & Massage（五星强推）": ("多分店", 10.78554, 106.69978),
    "Temple Leaf（按摩）": ("D1-D3", 10.78000, 106.69500),
    "BINGDOU Bingsu（牛油果冰淇淋）": ("Nguyễn Thị Minh Khai 路口", 12.24060, 109.19060),
    "Kem Bơ Vfruit（牛油果冰淇淋）": ("Nguyễn Thị Minh Khai 路口", 12.24060, 109.19060),
    "BÁNH CANH GHẸ CÔ BA MIỀN BIỂN（皮皮虾粗粉）": ("芽庄大教堂西北侧", 12.24750, 109.18720),
    "Luxury Anna Spa（芽庄按摩）": ("Bạch Đằng 街", 12.24470, 109.19490),
    "Ăn Thôi 2（米其林必比登越南菜）": ("64C Nguyễn Thị Minh Khai", 12.24060, 109.19060),
    "Mia 度假酒店（独栋院子+独立沙滩）": ("芽庄南部海岸", 12.19400, 109.21200),
    "Tyro Seafood Restaurant": ("芽庄海岸区", 12.23800, 109.19800),
    "Ot Hiem（越南菜）": ("芽庄市区", 12.24100, 109.19300),
    "Mộc Quán Seafood（海鲜大排档）": ("芽庄市区", 12.24300, 109.19300),
    "Quán ăn X.O（本地苍蝇馆子）": ("芽庄市区", 12.23500, 109.19600),
    "96 中国超市（旁旅行社换汇汇率3870）": ("芽庄市区", 12.24000, 109.19300),
}

CITY_BIAS = {"胡志明市": (10.776, 106.700), "芽庄": (12.239, 109.196), "岘港": (16.054, 108.202)}


def photon(q, city):
    blat, blon = CITY_BIAS.get(city, (10.8, 106.7))
    params = {"q": q, "limit": "3", "bbox": VN_BBOX, "lat": str(blat), "lon": str(blon)}
    url = "https://photon.komoot.io/api/?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            j = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []
    return [{
        "lat": f["geometry"]["coordinates"][1], "lon": f["geometry"]["coordinates"][0],
        "name": f["properties"].get("name") or "",
        "city": f["properties"].get("city") or "",
    } for f in j.get("features", [])]


def main():
    data = json.loads(IN_FILE.read_text(encoding="utf-8"))
    by_disp = {d["display"]: d for d in data}

    fixed, manual = [], []
    for d in data:
        disp = d["display"]
        # 1) 知识坐标
        if disp in KNOW:
            lat, lon = KNOW[disp]
            d.update({"lat": lat, "lon": lon, "status": "ok", "precision": "knowledge",
                      "osm_name": disp, "approx": False})
            fixed.append(disp)
            continue
        # 2) 已 ok 且不在重试名单 → 保留
        if d.get("status") == "ok" and disp not in RETRY:
            d.setdefault("precision", "photon")
            continue
        # 3) 重试查询
        hit = None
        for q in RETRY.get(disp, []):
            res = photon(q, d["city"])
            if res:
                hit = res[0]
                break
            time.sleep(0.35)
        if hit:
            d.update({"lat": hit["lat"], "lon": hit["lon"], "status": "ok",
                      "precision": "photon-retry", "osm_name": hit["name"], "approx": False})
            fixed.append(disp + " [retry]")
            time.sleep(0.35)
            continue
        # 4) 近似挂靠
        if disp in APPROX:
            hint, lat, lon = APPROX[disp]
            d.update({"lat": lat, "lon": lon, "status": "ok", "precision": "approx",
                      "osm_name": hint, "approx": True})
            fixed.append(disp + " [approx]")
        else:
            d["status"] = "needs_manual"
            manual.append(disp)

    OUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for d in data if d.get("status") == "ok")
    ap = sum(1 for d in data if d.get("status") == "ok" and d.get("approx"))
    print(f"最终: ok={ok} (其中近似 {ap}) needs_manual={len(manual)}")
    print("\n修复项:")
    for f in fixed:
        print("  ", f)
    print("\n需手动定位:")
    for m in manual:
        print("  ", m)


if __name__ == "__main__":
    main()
