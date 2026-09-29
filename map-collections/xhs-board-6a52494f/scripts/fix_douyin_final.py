# -*- coding: utf-8 -*-
"""抖音批次 5 家店的最终精确定位（Nominatim 查证结果）。"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FINAL = BASE / "osm_geocoded_final.json"

FIX = {
    "Phở Hưng 阿雄牛肉粉（四大天王）": {
        "lat": 10.75638, "lon": 106.67692, "precision": "nominatim-building", "approx": False,
        "osm_name": "Phở Hưng",
        "address": "241-243 Nguyễn Trãi, Q1（米其林推荐, 6:00-次日3:00）"},
    "Phở Lẽ 锦利牛肉粉（四大天王）": {
        "lat": 10.75525, "lon": 106.67353, "precision": "nominatim-poi", "approx": False,
        "osm_name": "Phở Lệ",
        "address": "413-415 Nguyễn Trãi, Q5 老店（米其林必比登）/ 分店 303-305 Võ Văn Tần, Q3"},
    "Bún Mọc Thanh Mai（清汤粉）": {
        "lat": 10.7730, "lon": 106.6952, "precision": "street-estimate", "approx": True,
        "osm_name": "Trương Định 街起点",
        "address": "14 Trương Định, Bến Thành, Q1（滨城市场西侧）"},
    "Cò Tú Cà Mau（越南海鲜）": {
        "lat": 10.7905, "lon": 106.6950, "precision": "street-estimate", "approx": True,
        "osm_name": "Hoàng Sa 街中段",
        "address": "219 Hoàng Sa, Tân Định, Q1（粉红教堂以北运河边）"},
    "Sầu Riêng Nguyên Ký 榴莲一条街": {
        "lat": 10.7700, "lon": 106.6950, "precision": "approx", "approx": True,
        "osm_name": "位置按视频确认",
        "address": "Sầu riêng Nguyên Ký（华人店,猫山王约40rmb/kg,街名待确认）"},
}

data = json.loads(FINAL.read_text(encoding="utf-8"))
for d in data:
    if d["display"] in FIX:
        d.update(FIX[d["display"]])
        print(f"  ✓ {d['display'][:30]:32s} -> {d['lat']:.5f},{d['lon']:.5f} [{d['precision']}]")
FINAL.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n总点位: {sum(1 for d in data if d.get('status') == 'ok')}")
