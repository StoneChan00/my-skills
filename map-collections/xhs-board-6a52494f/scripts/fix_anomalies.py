# -*- coding: utf-8 -*-
"""修复城市异常点位：强制使用近似挂靠坐标（描述列保留提示）。"""
import json
from pathlib import Path

F = Path(r"D:\2_Projects\github\StoneChan00\my-skills\map-collections\xhs-board-6a52494f\osm_geocoded_final.json")
data = json.loads(F.read_text(encoding="utf-8"))

FIX = {
    "Lvoire Pastry（第一甜品店）": ("柏悦酒店附近(D1)", 10.77890, 106.70050),
    "Bếp Cuốn Sài Gòn（米其林越南菜）": ("D1 中心区", 10.77700, 106.70000),
    "7 Bridges Brewing Co（西贡精酿）": ("一区", 10.77500, 106.70100),
    "Sa Spa（1区）": ("D1", 10.78500, 106.69900),
    "Phaya Thai Spa Quận 1": ("D1", 10.78000, 106.70300),
    "Xíu Spa": ("D1", 10.77500, 106.70000),
    "An's Spa & Massage（五星强推）": ("多分店(D1)", 10.78554, 106.69978),
    "Temple Leaf（按摩）": ("D1-D3", 10.78000, 106.69500),
    "BINGDOU Bingsu（牛油果冰淇淋）": ("Nguyễn Thị Minh Khai 路口", 12.24060, 109.19060),
    "BÁNH CANH GHẸ CÔ BA MIỀN BIỂN（皮皮虾粗粉）": ("芽庄大教堂西北侧", 12.24750, 109.18720),
    "Ăn Thôi 2（米其林必比登越南菜）": ("64C Nguyễn Thị Minh Khai", 12.24060, 109.19060),
    "Pizza 4P's": ("芽庄市区中心", 12.23850, 109.19300),
    "La Viet Coffee（亚洲第六咖啡店）": ("芽庄市区", 12.23800, 109.19200),
    "Quán ăn X.O（本地苍蝇馆子）": ("芽庄市区", 12.23500, 109.19600),
}

n = 0
for d in data:
    if d["display"] in FIX:
        hint, lat, lon = FIX[d["display"]]
        d.update({"lat": lat, "lon": lon, "status": "ok", "precision": "approx",
                  "osm_name": hint, "approx": True})
        n += 1

F.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"修复 {n} 个异常点位 -> 近似坐标")
