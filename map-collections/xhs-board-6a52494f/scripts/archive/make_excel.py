#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 geocoded.json 生成高德「地图小程序」批量导入 Excel（wia.amap.com PC 端上传）。

列结构（对齐官方批量导入模板字段: 名称/经纬度/地址/颜色/描述/文件夹）:
  名称   = POI 名称（地图上展示）
  经纬度 = "lng,lat"（高德坐标 GCJ-02，来自 POI 搜索）
  地址   = 规范地址（省市区+详细地址）
  颜色   = 1-8 数字，按分类着色
  描述   = 来源笔记 + 分类说明
  文件夹 = 一级分类文件夹（景点/美食/…）

用法: python make_excel.py
"""
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

BASE = Path(__file__).resolve().parent.parent
GEO_FILE = BASE / "geocoded.json"
OUT_FILE = BASE / "amap-import.xlsx"

HEADERS = ["名称", "经纬度", "地址", "颜色", "描述", "文件夹"]
# 官方模板颜色为 1-8 数字（前端色板从左到右），按分类映射
COLOR_MAP = {"景点": 1, "美食": 6, "住宿": 3, "购物": 5, "交通": 4, "其他": 7}
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")


def main() -> int:
    if not GEO_FILE.exists():
        print(f"[ERROR] 找不到 {GEO_FILE}，请先运行 geocode_amap.py")
        return 1

    data = json.loads(GEO_FILE.read_text(encoding="utf-8"))

    wb = Workbook()
    ws = wb.active
    ws.title = "导入数据"
    ws.append(HEADERS)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center")

    # 按 poiid 去重（不同笔记推荐同一地点时合并来源）
    seen, dropped = {}, 0
    rows = []
    for item in data:
        if item.get("status") not in ("ok", "ok_nocity"):
            continue
        m = item["matched"]
        poiid = m.get("poiid") or m.get("location")
        if poiid in seen:
            # 合并来源到已有行
            old = seen[poiid]
            srcs = set(old["desc"].split(" | ")) | {f"《{n}》" for n in item.get("notes", [])}
            old["desc"] = " | ".join(sorted(srcs))
            dropped += 1
            continue
        # 规范地址: 省+市+区+详细
        addr_parts = [p for p in (m.get("pname"), m.get("cityname"), m.get("adname")) if p and p != m.get("pname")]
        addr = ("".join(addr_parts) + (m.get("address") or "")).replace("[]", "")
        row = {
            "name": m.get("name") or item["name"],
            "loc": m.get("location", ""),
            "addr": addr,
            "color": COLOR_MAP.get(item.get("category", "其他"), 7),
            "desc": " | ".join(f"《{n}》" for n in item.get("notes", [])) or item["name"],
            "folder": item.get("category", "其他"),
        }
        seen[poiid] = row
        rows.append(row)

    for r in rows:
        ws.append([r["name"], r["loc"], r["addr"], r["color"], r["desc"], r["folder"]])

    # 列宽
    for col, w in zip("ABCDEF", (28, 20, 50, 6, 40, 10)):
        ws.column_dimensions[col].width = w

    wb.save(OUT_FILE)
    print(f"生成 {OUT_FILE}")
    print(f"共 {len(rows)} 个点位（合并重复 {dropped} 条）")
    folders = {}
    for r in rows:
        folders[r["folder"]] = folders.get(r["folder"], 0) + 1
    print("文件夹分布:", json.dumps(folders, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
