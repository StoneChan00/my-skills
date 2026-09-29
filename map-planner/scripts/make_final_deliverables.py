# -*- coding: utf-8 -*-
"""生成 Google My Maps 批量导入文件（CSV）+ 增强版分享地图 HTML（含高德导航深链）。"""
import csv
import json
from pathlib import Path

import _common
BASE = _common.base_from_argv()  # --dir <collection目录> 可指定，缺省取最新
GEO = BASE / "osm_geocoded_final.json"
data = [d for d in json.loads(GEO.read_text(encoding="utf-8")) if d.get("status") == "ok"]

city_order = {"胡志明市": 0, "芽庄": 1, "岘港": 2}
cat_order = {"景点": 0, "美食": 1, "按摩": 2, "住宿": 3, "购物": 4, "交通": 5}
data.sort(key=lambda d: (city_order.get(d["city"], 9), cat_order.get(d["category"], 9)))

# ---------- 1) Google My Maps CSV ----------
csv_path = BASE / "google-mymaps.csv"
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["Name", "Latitude", "Longitude", "Description", "City", "Category"])
    for d in data:
        desc = " | ".join(f"《{n}》" for n in d.get("notes", []))
        if d.get("approx"):
            desc += f"｜⚠位置约为{d.get('osm_name', '')}附近"
        if d.get("address"):
            desc += f"｜{d['address']}"
        w.writerow([d["display"], f"{d['lat']:.6f}", f"{d['lon']:.6f}",
                    desc[:500], d["city"], d["category"]])
print(f"CSV: {csv_path.name} ({len(data)} 行)")

# ---------- 2) 增强版 HTML（高德深链 + 更好用） ----------
COLORS = {"景点": "#1E88E5", "美食": "#FB8C00", "按摩": "#8E24AA", "住宿": "#43A047",
          "购物": "#E53935", "交通": "#00897B"}
ICONS = {"景点": "🏛", "美食": "🍜", "按摩": "💆", "住宿": "🏨", "购物": "🛍", "交通": "🚕"}

points = []
for d in data:
    notes = "、".join(f"《{n}》" for n in d.get("notes", [])[:3])
    points.append({
        "name": d["display"], "lat": d["lat"], "lon": d["lon"],
        "cat": d["category"], "city": d["city"],
        "color": COLORS.get(d["category"], "#757575"),
        "icon": ICONS.get(d["category"], "📍"),
        "approx": bool(d.get("approx")),
        "notes": notes, "addr": d.get("address") or d.get("osm_name") or "",
    })

html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🇻🇳 越南旅行地图 · 82 地点</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body { margin: 0; font-family: "Microsoft YaHei", -apple-system, sans-serif; }
  #map { width: 100vw; height: 100vh; }
  .panel { position: fixed; top: 12px; right: 12px; z-index: 1000; background: #fff; border-radius: 14px;
           padding: 14px 16px; box-shadow: 0 2px 14px rgba(0,0,0,.2); max-width: 280px; }
  .panel h3 { margin: 0 0 8px; font-size: 15px; }
  .btn { display: inline-block; margin: 3px 4px 3px 0; padding: 4px 10px; border-radius: 14px;
         border: 1px solid #ddd; cursor: pointer; font-size: 12px; background: #fafafa; user-select: none; }
  .btn.on { background: #1F4E79; color: #fff; border-color: #1F4E79; }
  .stat { font-size: 12px; color: #777; margin-top: 4px; }
  .pin { text-align: center; }
  .pin .dot { width: 26px; height: 26px; border-radius: 50%; border: 2px solid #fff;
              box-shadow: 0 1px 5px rgba(0,0,0,.45); display: flex; align-items: center;
              justify-content: center; font-size: 14px; margin: 0 auto; }
  .pin span.lbl { display: block; font-size: 11px; color: #333; background: rgba(255,255,255,.92);
                  border-radius: 8px; padding: 0 5px; margin-top: 2px; white-space: nowrap; }
  .pop-title { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
  .pop-meta { font-size: 12px; color: #666; margin-bottom: 2px; max-width: 230px; }
  .pop-warn { color: #E65100; font-size: 12px; }
  .nav-btn { display: inline-block; margin-top: 6px; padding: 5px 12px; background: #1F4E79; color: #fff;
             border-radius: 16px; text-decoration: none; font-size: 12px; }
  .nav-btn:active { background: #163a5c; }
</style>
</head>
<body>
<div id="map"></div>
<div class="panel">
  <h3>🇻🇳 越南旅行地图</h3>
  <div id="cityFilter"></div>
  <div id="catFilter" style="margin-top:4px"></div>
  <div class="stat" id="stat"></div>
  <div class="stat" style="color:#999">点标记可查看详情 + 🧭高德导航</div>
</div>
<script>
const POINTS = __POINTS__;
const map = L.map("map").setView([12.3, 107.9], 6);
L.tileLayer("https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}", {
  subdomains: "1234", maxZoom: 19, attribution: "高德"
}).addTo(map);

const markers = [];
POINTS.forEach(p => {
  const navUrl = "https://uri.amap.com/marker?position=" + p.lon + "," + p.lat +
                 "&name=" + encodeURIComponent(p.name) + "&src=VietnamTripMap&callnative=1";
  const m = L.marker([p.lat, p.lon], { icon: L.divIcon({ className: "",
    html: '<div class="pin"><div class="dot" style="background:' + p.color + '">' + p.icon +
          '</div><span class="lbl">' + p.name.slice(0, 14) + '</span></div>',
    iconSize: [26, 44], iconAnchor: [13, 30], popupAnchor: [0, -28] }) }).bindPopup(
    '<div class="pop-title">' + (p.approx ? "⚠ " : "") + p.name + '</div>' +
    '<div class="pop-meta">🏷 ' + p.city + ' · ' + p.cat + (p.approx ? " · 近似定位" : "") + '</div>' +
    (p.addr ? '<div class="pop-meta">📍 ' + p.addr + '</div>' : "") +
    (p.notes ? '<div class="pop-meta">来源：' + p.notes + '</div>' : "") +
    (p.approx ? '<div class="pop-warn">位置约为附近区域</div>' : "") +
    '<a class="nav-btn" target="_blank" href="' + navUrl + '">🧭 高德App打开/导航</a>'
  );
  m.cat = p.cat; m.city = p.city;
  markers.push(m); m.addTo(map);
});

const state = { cat: "全部", city: "全部" };
function apply() {
  markers.forEach(m => {
    const ok = (state.cat === "全部" || m.cat === state.cat) &&
               (state.city === "全部" || m.city === state.city);
    ok ? map.addLayer(m) : map.removeLayer(m);
  });
  const n = markers.filter(m => map.hasLayer(m)).length;
  document.getElementById("stat").textContent = "显示 " + n + " / " + POINTS.length + " 个地点";
}
function mk(el, options, key) {
  el.innerHTML = "";
  options.forEach(o => {
    const b = document.createElement("span");
    b.className = "btn" + (state[key] === o ? " on" : "");
    b.textContent = o;
    b.onclick = () => { state[key] = o; apply(); mk(el, options, key); };
    el.appendChild(b);
  });
}
mk(document.getElementById("cityFilter"), ["全部", "胡志明市", "芽庄", "岘港"], "city");
const cf = document.getElementById("catFilter");
["全部"].concat(Object.keys({景点:0,美食:0,按摩:0,住宿:0,购物:0,交通:0})).forEach(c => {
  const b = document.createElement("span");
  b.className = "btn" + (state.cat === c ? " on" : "");
  b.textContent = c;
  b.onclick = () => { state.cat = c; apply();
    [...cf.children].forEach(x => x.classList.remove("on")); b.classList.add("on"); };
  cf.appendChild(b);
});
apply();
</script>
</body>
</html>"""

html = html.replace("__POINTS__", json.dumps(points, ensure_ascii=False))
out = BASE / "vietnam-map.html"
out.write_text(html, encoding="utf-8")
print(f"HTML: {out.name} ({len(points)} 点位, 含高德导航深链)")
