# -*- coding: utf-8 -*-
"""
生成交付物（v2）：
  1. google-mymaps.csv  — Google My Maps 批量导入
  2. <name>-map.html    — Leaflet 网页地图（多图层/定位/一键导航）

HTML 特性：
  - 图层：卫星+路网（默认，海外覆盖完整）/ 标准矢量（国内）/ OSM（备选）
  - 定位按钮（HTML5 Geolocation，需 HTTPS 或 localhost）
  - 每个点位双按钮：🧭 导航前往（唤起高德App导航）/ 📍 查看位置
  - 城市/分类筛选、来源笔记、近似标记
用法: python make_final_deliverables.py [--dir <collection目录>]
"""
import _common
import csv
import json
from pathlib import Path

BASE = _common.base_from_argv()
GEO = BASE / "osm_geocoded_final.json"
data = [d for d in json.loads(GEO.read_text(encoding="utf-8")) if d.get("status") == "ok"]

# 海外检测（中国大致范围 lon 73.5-135.5, lat 17.5-53.6）→ 默认用卫星+路网
OVERSEAS = any(p["lat"] < 17.5 or p["lat"] > 53.6 or p["lon"] < 73.5 or p["lon"] > 135.5 for p in data)

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

# ---------- 2) 网页地图 ----------
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

# 初始视野：所有点的外接范围
lats = [p["lat"] for p in points]
lons = [p["lon"] for p in points]
center = f"[{(max(lats) + min(lats)) / 2:.4f}, {(max(lons) + min(lons)) / 2:.4f}]"
span = max(max(lats) - min(lats), (max(lons) - min(lons)) * 0.9)
zoom = 6 if span > 5 else (8 if span > 2 else (10 if span > 0.8 else 12))

html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🇻🇳 越南旅行地图</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body { margin: 0; font-family: "Microsoft YaHei", -apple-system, sans-serif; }
  #map { width: 100vw; height: 100vh; }
  .panel { position: fixed; top: 12px; right: 12px; z-index: 1000; background: #fff; border-radius: 14px;
           padding: 12px 14px; box-shadow: 0 2px 14px rgba(0,0,0,.2); max-width: 260px; }
  .panel h3 { margin: 0 0 6px; font-size: 15px; }
  .btn { display: inline-block; margin: 2px 4px 2px 0; padding: 3px 10px; border-radius: 14px;
         border: 1px solid #ddd; cursor: pointer; font-size: 12px; background: #fafafa; user-select: none; }
  .btn.on { background: #1F4E79; color: #fff; border-color: #1F4E79; }
  .stat { font-size: 12px; color: #777; margin-top: 4px; }
  .hint { font-size: 11px; color: #999; margin-top: 4px; }
  .pin { text-align: center; }
  .pin .dot { width: 26px; height: 26px; border-radius: 50%; border: 2px solid #fff;
              box-shadow: 0 1px 5px rgba(0,0,0,.45); display: flex; align-items: center;
              justify-content: center; font-size: 14px; margin: 0 auto; }
  .pin span.lbl { display: block; font-size: 11px; color: #333; background: rgba(255,255,255,.92);
                  border-radius: 8px; padding: 0 5px; margin-top: 2px; white-space: nowrap; }
  .pop-title { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
  .pop-meta { font-size: 12px; color: #666; margin-bottom: 2px; max-width: 230px; }
  .pop-warn { color: #E65100; font-size: 12px; }
  .pop-actions { margin-top: 8px; }
  .nav-btn { display: inline-block; padding: 6px 14px; border-radius: 16px; text-decoration: none;
             font-size: 13px; margin-right: 6px; }
  .nav-primary { background: #1F4E79; color: #fff; }
  .nav-secondary { background: #fff; color: #1F4E79; border: 1px solid #1F4E79; }
  .nav-btn:active { opacity: .85; }
  .locate-btn { position: fixed; bottom: 24px; right: 12px; z-index: 1000; width: 44px; height: 44px;
                background: #fff; border: 2px solid rgba(0,0,0,.25); border-radius: 50%; cursor: pointer;
                font-size: 20px; line-height: 40px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,.3); }
  .locate-btn.locating { animation: pulse 1s infinite; }
  @keyframes pulse { 50% { background: #cce5ff; } }
  .toast { position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%); z-index: 2000;
           background: rgba(0,0,0,.75); color: #fff; border-radius: 8px; padding: 8px 16px;
           font-size: 13px; display: none; }
</style>
</head>
<body>
<div id="map"></div>
<div class="panel">
  <h3>🇻🇳 越南旅行地图</h3>
  <div id="cityFilter"></div>
  <div id="catFilter" style="margin-top:4px"></div>
  <div class="stat" id="stat"></div>
  <div class="hint">点标记查看详情 · 🧭一键导航 · 右下角📍定位</div>
</div>
<div class="locate-btn" id="locateBtn" title="定位到我">📍</div>
<div class="toast" id="toast"></div>
<script>
const POINTS = __POINTS__;
const OVERSEAS = __OVERSEAS__;
const map = L.map("map").setView(__CENTER__, __ZOOM__);

// ---- 图层（高德瓦片国内直连；卫星+路网对海外覆盖完整）----
const amapVec = L.tileLayer("https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}",
  { subdomains: "1234", maxZoom: 19, attribution: "高德" });
const amapSat = L.tileLayer("https://wprd0{s}.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=7",
  { subdomains: "1234", maxZoom: 19, attribution: "高德卫星" });
const amapRoad = L.tileLayer("https://wprd0{s}.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=8",
  { subdomains: "1234", maxZoom: 19, attribution: "高德路网" });
const osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png",
  { maxZoom: 19, attribution: "OSM" });

const satGroup = L.layerGroup([amapSat, amapRoad]);
const layers = { "🗺 标准": amapVec, "🛰 卫星+路网": satGroup, "🛰 纯卫星": amapSat, "🌍 OSM": osm };
L.control.layers(layers, null, { position: "bottomleft" }).addTo(map);
(OVERSEAS ? satGroup : amapVec).addTo(map);

// ---- 标记 ----
const markers = [];
POINTS.forEach(p => {
  const navUrl = "https://uri.amap.com/navigation?to=" + p.lon + "," + p.lat + "," +
                 encodeURIComponent(p.name) + "&mode=car&policy=1&src=VietnamTripMap&callnative=1";
  const viewUrl = "https://uri.amap.com/marker?position=" + p.lon + "," + p.lat +
                  "&name=" + encodeURIComponent(p.name) + "&src=VietnamTripMap&callnative=1";
  const m = L.marker([p.lat, p.lon], { icon: L.divIcon({ className: "",
    html: '<div class="pin"><div class="dot" style="background:' + p.color + '">' + p.icon +
          '</div><span class="lbl">' + p.name.slice(0, 14) + '</span></div>',
    iconSize: [26, 44], iconAnchor: [13, 30], popupAnchor: [0, -28] }) }).bindPopup(
    '<div class="pop-title">' + (p.approx ? "⚠ " : "") + p.name + '</div>' +
    '<div class="pop-meta">🏷 ' + p.city + ' · ' + p.cat + (p.approx ? " · 近似定位" : "") + '</div>' +
    (p.addr ? '<div class="pop-meta">📍 ' + p.addr + '</div>' : "") +
    (p.notes ? '<div class="pop-meta">来源：' + p.notes + '</div>' : "") +
    (p.approx ? '<div class="pop-warn">位置约为附近区域，建议到后按名称搜索确认</div>' : "") +
    '<div class="pop-actions">' +
    '<a class="nav-btn nav-primary" target="_blank" href="' + navUrl + '">🧭 导航前往</a>' +
    '<a class="nav-btn nav-secondary" target="_blank" href="' + viewUrl + '">📍 查看位置</a>' +
    '</div>', { maxWidth: 280 });
  m.cat = p.cat; m.city = p.city;
  markers.push(m); m.addTo(map);
});

// ---- 筛选 ----
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
mk(document.getElementById("cityFilter"), ["全部"].concat(Array.from(new Set(POINTS.map(p => p.city)))), "city");
const cf = document.getElementById("catFilter");
["全部", "景点", "美食", "按摩", "住宿", "购物", "交通"].forEach(c => {
  const b = document.createElement("span");
  b.className = "btn" + (state.cat === c ? " on" : "");
  b.textContent = c;
  b.onclick = () => { state.cat = c; apply();
    Array.from(cf.children).forEach(x => x.classList.remove("on")); b.classList.add("on"); };
  cf.appendChild(b);
});
apply();

// ---- 定位 ----
const locBtn = document.getElementById("locateBtn");
const toast = document.getElementById("toast");
let userMarker = null, accuracyCircle = null;
function showToast(msg, ms) {
  toast.textContent = msg; toast.style.display = "block";
  setTimeout(() => { toast.style.display = "none"; }, ms || 2500);
}
locBtn.onclick = () => {
  if (!navigator.geolocation) { showToast("此浏览器不支持定位"); return; }
  locBtn.classList.add("locating");
  locBtn.textContent = "⏳";
  map.locate({ setView: true, maxZoom: 16, enableHighAccuracy: true, timeout: 10000 });
};
map.on("locationfound", e => {
  locBtn.classList.remove("locating"); locBtn.textContent = "📍";
  if (userMarker) { map.removeLayer(userMarker); map.removeLayer(accuracyCircle); }
  userMarker = L.circleMarker([e.latlng.lat, e.latlng.lng], { radius: 8, color: "#136AEC",
    fillColor: "#136AEC", fillOpacity: 0.9, weight: 2 }).addTo(map)
    .bindPopup("📍 我的位置").openPopup();
  accuracyCircle = L.circle([e.latlng.lat, e.latlng.lng], {
    radius: e.accuracy / 2, color: "#136AEC", weight: 1, fillOpacity: 0.1 }).addTo(map);
});
map.on("locationerror", e => {
  locBtn.classList.remove("locating"); locBtn.textContent = "📍";
  const msgs = { 1: "定位权限被拒绝，请在浏览器设置允许位置权限", 2: "位置信息不可用",
                 3: "定位超时，请重试" };
  showToast(msgs[e.code] || "定位失败");
});
</script>
</body>
</html>"""

html = (html
        .replace("__POINTS__", json.dumps(points, ensure_ascii=False))
        .replace("__OVERSEAS__", "true" if OVERSEAS else "false")
        .replace("__CENTER__", center)
        .replace("__ZOOM__", str(zoom)))
out = BASE / "vietnam-map.html"
out.write_text(html, encoding="utf-8")
print(f"HTML: {out.name} ({len(points)} 点位, 默认图层={'卫星+路网' if OVERSEAS else '标准'}, 定位+一键导航)")
