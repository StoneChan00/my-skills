# -*- coding: utf-8 -*-
"""生成 Leaflet 预览地图 HTML（高德瓦片国内直连可用，海外无偏移）。"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
IN_FILE = BASE / "osm_geocoded_final.json"
OUT_FILE = BASE / "preview-map.html"

data = [d for d in json.loads(IN_FILE.read_text(encoding="utf-8")) if d.get("status") == "ok"]

COLORS = {"景点": "#1E88E5", "美食": "#FB8C00", "按摩": "#8E24AA", "住宿": "#43A047", "购物": "#E53935", "交通": "#00897B"}
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
        "notes": notes,
        "addr": d.get("address") or d.get("osm_name") or "",
        "precision": d.get("precision", ""),
    })

# 城市中心用于初始视野
CITY_CENTER = {"胡志明市": [10.776, 106.700, 12], "芽庄": [12.239, 109.196, 13], "岘港": [16.054, 108.202, 13]}

html = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>越南旅行合集 · 82 地点预览</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  body { margin: 0; font-family: "Microsoft YaHei", sans-serif; }
  #map { width: 100vw; height: 100vh; }
  .panel { position: fixed; top: 12px; right: 12px; z-index: 1000; background: #fff; border-radius: 12px;
           padding: 14px 16px; box-shadow: 0 2px 12px rgba(0,0,0,.18); max-width: 300px; }
  .panel h3 { margin: 0 0 8px; font-size: 15px; }
  .btn { display: inline-block; margin: 3px 4px 3px 0; padding: 4px 10px; border-radius: 14px; border: 1px solid #ddd;
         cursor: pointer; font-size: 12px; background: #fafafa; }
  .btn.on { background: #1F4E79; color: #fff; border-color: #1F4E79; }
  .legend { font-size: 12px; color: #555; margin-top: 6px; }
  .legend i { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }
  .stat { font-size: 12px; color: #777; }
  .pin { text-align: center; font-size: 18px; }
  .pin span { display: block; font-size: 11px; color: #333; background: rgba(255,255,255,.9); border-radius: 8px;
              padding: 0 4px; margin-top: 1px; white-space: nowrap; }
  .pop-title { font-weight: bold; font-size: 14px; margin-bottom: 4px; }
  .pop-meta { font-size: 12px; color: #666; margin-bottom: 2px; }
  .pop-warn { color: #E65100; font-size: 12px; }
</style>
</head>
<body>
<div id="map"></div>
<div class="panel">
  <h3>🇻🇳 越南旅行合集 · 预览</h3>
  <div id="filters"></div>
  <div class="legend" id="legend"></div>
  <div class="stat" id="stat"></div>
</div>
<script>
const POINTS = __POINTS__;
const CITY_CENTER = __CENTER__;
const CATS = ["景点", "美食", "按摩", "住宿", "购物", "交通"];

const map = L.map("map").setView([12.5, 107.8], 6);
L.tileLayer("https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}", {
  subdomains: "1234", maxZoom: 19, attribution: "高德世界地图"
}).addTo(map);

const markers = [];
function markerIcon(p, dim) {
  return L.divIcon({
    className: "",
    html: `<div class="pin"><div style="width:26px;height:26px;border-radius:50%;background:${p.color};
            border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4);display:flex;align-items:center;
            justify-content:center;font-size:14px">${p.icon}</div>${dim ? "" :
            `<span>${p.name.slice(0, 12)}</span>`}</div>`,
    iconSize: [26, 40], iconAnchor: [13, 28], popupAnchor: [0, -26]
  });
}
POINTS.forEach(p => {
  const m = L.marker([p.lat, p.lon], { icon: markerIcon(p) }).bindPopup(
    `<div class="pop-title">${p.approx ? "⚠ " : ""}${p.name}</div>` +
    `<div class="pop-meta">🏷 ${p.city} · ${p.cat} ${p.approx ? "· 近似定位" : ""}</div>` +
    (p.addr ? `<div class="pop-meta">📍 ${p.addr}</div>` : "") +
    (p.notes ? `<div class="pop-meta">来源：${p.notes}</div>` : "") +
    (p.approx ? `<div class="pop-warn">位置约为附近区域，导入高德后建议手动微调</div>` : "")
  );
  m.cat = p.cat; m.city = p.city;
  markers.push(m); m.addTo(map);
});

const state = { cat: "全部", city: "全部" };
function apply() {
  markers.forEach(m => {
    const ok = (state.cat === "全部" || m.cat === state.cat) && (state.city === "全部" || m.city === state.city);
    ok ? map.addLayer(m) : map.removeLayer(m);
  });
  const n = markers.filter(m => map.hasLayer(m)).length;
  document.getElementById("stat").textContent = `显示 ${n} / ${POINTS.length} 个地点（⚠ 近似 ${POINTS.filter(p => p.approx).length}）`;
}
function makeFilter(el, options, key) {
  el.innerHTML = "";
  options.forEach(o => {
    const b = document.createElement("span");
    b.className = "btn" + (state[key] === o ? " on" : "");
    b.textContent = o; b.onclick = () => { state[key] = o; apply(); makeFilter(el, options, key); };
    el.appendChild(b);
  });
}
makeFilter(document.getElementById("filters"), ["全部", "胡志明市", "芽庄", "岘港"], "city");
const lg = document.getElementById("legend");
CATS.forEach(c => {
  const s = document.createElement("span");
  s.className = "btn"; s.textContent = c; s.style.borderColor = "transparent";
  s.onclick = () => { state.cat = state.cat === c ? "全部" : c; apply();
    [...lg.children].forEach(x => x.classList.remove("on")); if (state.cat === c) s.classList.add("on"); };
  s.innerHTML = `<i style="background:${POINTS.find(p => p.cat === c)?.color || "#999"}"></i>${c}`;
  lg.appendChild(s);
});
apply();
</script>
</body>
</html>"""

html = html.replace("__POINTS__", json.dumps(points, ensure_ascii=False))
html = html.replace("__CENTER__", json.dumps(CITY_CENTER))
OUT_FILE.write_text(html, encoding="utf-8")
print(f"生成 {OUT_FILE} ({len(points)} 点位)")
