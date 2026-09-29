#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高德 POI 搜索定位：把 locations.json 中的地点转成精确 POI（名称/地址/经纬度/poiid）。

用法:
  python geocode_amap.py --test    # 仅测试 key 是否可用
  python geocode_amap.py           # 正式跑（增量 + 缓存，可重复执行）

输入: ../locations.json  [{"name": "故宫", "city": "北京", "category": "景点", "notes": ["笔记标题"]}, ...]
输出: ../geocoded.json   [{"name", "city", "category", "status", "matched": {poi fields}, "candidates": [...]}, ...]

注意:
  - 去重逻辑在生成 locations.json 时完成（同地点合并，notes 累积）
  - 已成功的条目不会重复调用 API（增量缓存）
  - QPS 限制: 间隔 350ms；配额错误(infocode 10044)会停止并提示
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import _common
BASE = _common.base_from_argv()  # --dir <collection目录> 可指定，缺省取最新
LOC_FILE = BASE / "locations.json"
GEO_FILE = BASE / "geocoded.json"
CONFIG = _common.config_path()

SLEEP_S = 0.35  # 保守 QPS (~2.8/s，个人开发者搜索 QPS 上限 3)


def get_key() -> str:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    return cfg["amap_key"]


def place_text(key: str, keywords: str, city: str = None, timeout: int = 15) -> dict:
    params = {"keywords": keywords, "key": key, "offset": 5, "page": 1}
    if city:
        params["city"] = city
    url = "https://restapi.amap.com/v3/place/text?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def test_key() -> int:
    key = get_key()
    print(f"key: {key[:6]}****（已从 config.json 读取）")
    try:
        data = place_text(key, "故宫", city="北京")
    except Exception as e:
        print(f"[FAIL] 请求异常: {e}")
        return 1
    if data.get("status") != "1":
        print(f"[FAIL] status={data.get('status')} infocode={data.get('infocode')} {data.get('info')}")
        return 1
    pois = data.get("pois") or []
    print(f"[OK] 搜索成功，status=1，返回 {len(pois)} 个 POI")
    if pois:
        p = pois[0]
        print(f"     示例: {p.get('name')} | {p.get('address')} | {p.get('location')} | city={p.get('cityname')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="仅测试 key")
    args = ap.parse_args()

    if args.test:
        return test_key()

    if not LOC_FILE.exists():
        print(f"[ERROR] 找不到 {LOC_FILE}，请先生成 locations.json")
        return 1

    key = get_key()
    locations = json.loads(LOC_FILE.read_text(encoding="utf-8"))

    # 载入已有结果（增量缓存）
    results = {}
    if GEO_FILE.exists():
        for item in json.loads(GEO_FILE.read_text(encoding="utf-8")):
            if item.get("status") == "ok":
                results[(item["name"], item.get("city") or "")] = item

    out, ok, fail, skipped = [], 0, 0, 0
    for loc in locations:
        name, city = loc["name"], loc.get("city") or ""
        cache_key = (name, city)
        if cache_key in results:
            out.append(results[cache_key])
            skipped += 1
            continue

        try:
            data = place_text(key, name, city=city)
        except Exception as e:
            print(f"  [ERR] {name}: 请求异常 {e}")
            data = {"status": "0", "info": str(e), "infocode": "NETWORK"}

        infocode = data.get("infocode", "")
        if infocode == "10044":
            print(f"[STOP] 个人配额用尽（10044）。未完成条目下次继续；或改用纯地址导入。")
            break
        if infocode == "10021":
            print(f"  [WAIT] QPS 超限，等 2s 重试: {name}")
            time.sleep(2)
            try:
                data = place_text(key, name, city=city)
            except Exception as e:
                data = {"status": "0", "info": str(e)}

        pois = data.get("pois") or []
        item = {"name": name, "city": city, "category": loc.get("category", "其他"),
                "notes": loc.get("notes", []), "raw": loc}
        if data.get("status") == "1" and pois:
            item["status"] = "ok"
            item["matched"] = {k: pois[0].get(k) for k in
                               ("name", "address", "location", "poiid", "type", "cityname", "pname", "adname")}
            item["candidates"] = [{"name": p.get("name"), "address": p.get("address"),
                                   "location": p.get("location")} for p in pois[1:4]]
            ok += 1
            print(f"  [OK] {name} -> {pois[0].get('name')} @ {pois[0].get('cityname') or ''} {pois[0].get('address')}")
        elif data.get("status") == "1":
            # 有城市限定搜不到 → 去掉城市全国搜
            try:
                data2 = place_text(key, name)
                pois2 = data2.get("pois") or []
            except Exception:
                pois2 = []
            if pois2:
                item["status"] = "ok_nocity"
                item["matched"] = {k: pois2[0].get(k) for k in
                                   ("name", "address", "location", "poiid", "type", "cityname", "pname", "adname")}
                item["candidates"] = []
                ok += 1
                print(f"  [OK*] {name} (全国搜索) -> {pois2[0].get('name')} @ {pois2[0].get('cityname')}")
            else:
                item["status"] = "no_match"
                fail += 1
                print(f"  [MISS] {name} (city={city or '全国'}) 无结果")
        else:
            item["status"] = f"error_{infocode}"
            item["info"] = data.get("info")
            fail += 1
            print(f"  [ERR] {name}: {data.get('info')} (infocode={infocode})")

        out.append(item)
        time.sleep(SLEEP_S)

    GEO_FILE.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n完成: ok={ok} miss/error={fail} 缓存跳过={skipped} 总计={len(locations)}")
    print(f"结果: {GEO_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
