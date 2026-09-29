# 越南旅行地点合集（小红书 + 抖音 → 高德 App 收藏）

> 来源：JoJo 的小红书共享专辑《越南》（36 篇笔记）+ 10 条抖音探店视频，覆盖胡志明/芽庄/岘港
> 成果：**91 个推荐地点** → 高德 App「越南」收藏夹（个人收藏，含分组）+ 网页地图 + My Maps CSV

## 目录结构

```
xhs-board-6a52494f/
├── README.md                    # 本文件
├── locations.json               # ★ 地点提取清单（中文名+查询名+分类+来源）
├── osm_geocoded_final.json      # ★ 最终定位数据（91 点，含精度标记）
├── notes_digest.json            # 笔记摘要（LLM 提取输入）
├── note_list.json / board.json  # 笔记列表（含 xsec_token）/ 合集元数据
├── amap_fav_data.json           # 高德 App 收藏灌入数据快照
├── vietnam-map.html             # ★ 交付：网页地图（高德瓦片+导航深链，免梯子）
├── google-mymaps.csv            # ★ 交付：Google My Maps 导入
├── amap-import-v3.xlsx          # 交付：地图小程序导入（仅国内坐标可用，海外见 README 说明）
├── 导入模板.xlsx                 # 高德官方批量导入模板（make_excel_v4.py 依赖）
├── notes/                       # [git-ignored] 36 篇笔记原始 JSON
├── data/                        # [git-ignored] 中间产物（聊天 dump、迭代定位数据）
├── captures/                    # [git-ignored] API 协议捕获样本（cloudSync 请求体）
├── artifacts/                   # [git-ignored] 截图、失败回传文件
└── scripts/                     # 本合集专用脚本（通用管线在 map-planner skill）
    ├── archive/                 #   被取代的历史版本
    └── debug/                   #   一次性探索/调试脚本
```

通用管线脚本已迁至 `map-planner/scripts/`（skill），均支持 `--dir` 指定本目录。

## 📦 交付物

| 文件 | 说明 |
|---|---|
| **高德 App「越南」收藏夹** | ★ 最终交付：91 点已灌入用户高德账号（个人收藏+分组，手机原生体验） |
| **vietnam-map.html** | ★ 网页地图：高德瓦片国内直连、分类着色、每点带高德 App 导航深链 |
| google-mymaps.csv | Google My Maps 导入（Name/Latitude/Longitude/Description，需梯子） |
| amap-import-v3.xlsx | 地图小程序批量导入（**仅国内坐标**——海外会被"经纬度字段无效"拒绝，故本合集实际走的是 App 收藏灌入路径） |

## 🗺️ 点位统计（91 个）

| 城市 | 景点 | 美食 | 按摩 | 住宿 | 购物 | 交通 | 小计 |
|---|---|---|---|---|---|---|---|
| 胡志明市 | 13 | 33 | 9 | 1 | 3 | 4 | **63** |
| 芽庄 | 4 | 17 | 1 | 2 | 2 | 1 | **27** |
| 岘港 | - | - | 1 | - | - | - | **1** |

- 坐标：OSM (WGS-84)，海外无 GCJ-02 偏移
- 精度：62 精确 + 29 近似（含 2 家米其林：Phở Hưng 阿雄、Phở Lẽ 锦利）
- 同坐标堆叠点已错开 5-30 米（高德 App 按墨卡托像素去重的预防措施）

## 🚀 使用方式

### 高德 App「越南」收藏夹（已完成，最终交付）
91 个地点已灌入高德账号个人收藏并归入"越南"分组：手机高德 App → 我的 → 收藏 → 越南。
点开任意地点即可导航。备注列含来源笔记与米其林/营业时间提示。

### 网页地图（分享给没梯子的朋友）
浏览器打开 `vietnam-map.html`（或 gh-pages 链接），支持城市/分类筛选，
每个点带 🧭 高德 App 导航深链。微信直接发文件或链接即可。

### Google My Maps（有梯子的朋友）
mymaps.google.com → 创建地图 → 导入 `google-mymaps.csv`（Name/Lat/Lng 列自动识别）→ 分享链接。

## 🔄 增量更新（如以后需要）

若日后 JoJo 又往聊天里分享了新笔记（`scripts/check_new_notes.py` 手动探测，`scripts/watcher.py` 可后台守望）：
```
1. scripts/check_new_notes.py → 并入 note_list.json
2. map-planner/scripts/read_notes.py --read-only --dir <本目录>
3. map-planner/scripts/make_digest.py → 人工/LLM 提取新地点 → locations.json 追加
4. map-planner/scripts/osm_geocode_v2.py + validate_coords.py + 本目录 scripts/ 下的修正脚本
5. map-planner/scripts/make_fav_data.py → 按 refs/amap-cloudsync.md 流程灌入
6. map-planner/scripts/make_final_deliverables.py → 刷新网页地图与 CSV
```

## 🧭 数据链路（实际走通的路径）

```
小红书私密共享专辑(board/note API 拒绝非所有者)
  └→ 所有者将笔记分享到聊天 → messages/history API 直调(免签名)
      → 笔记卡片 link 字段提取 xsec_token → redbook read 逐篇读取
抖音分享链接 → Playwright 匿名访问 → 标题/话题/AI章节摘要提取
  └→ LLM 提取 91 地点(含笔记内越南语地址)
      → Photon(komoot) 直连定位 + 知识坐标 + 近似挂靠 + 城市范围校验
      → 高德 App 个人收藏 cloudSync 捕获-重放 + 手机手动移动收尾
      → vietnam-map.html + google-mymaps.csv
```

## ⚠️ 已知坑（详见 worklog 2026-09-28 两篇）

- 高德 Web 服务 key 的海外搜索未开通(10002) → 用 OSM 系定位替代
- Nominatim 国内直连被干扰 → Photon 可直连；系统代理(7897)对 nominatim 也失效（分流规则）
- npm .cmd 垫片会切坏 cookie 里的分号 → node 直调 cli.js
- web_session 是 HttpOnly，检测登录态用 page.context().cookies() 而非 document.cookie
