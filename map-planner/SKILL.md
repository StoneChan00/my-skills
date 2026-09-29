# Map Planner: 社媒内容 → 地点合集 → 地图标点

**Description**: 从小红书（合集/笔记）、抖音（分享链接）等内容源批量提取推荐地点，
地理编码定位后生成多目标交付物：高德 App 个人收藏（含收藏夹分组）、高德地图小程序
批量导入 Excel（国内）、Google My Maps CSV、Leaflet 网页地图（免梯子可分享）。
内置高德 cloudSync 协议捕获-重放能力，可把任意海外/国内坐标批量灌入高德 App 收藏。

**Use when**: 用户提出以下需求时触发：
- 从小红书/抖音内容中提取地点、做地点合集、地图标点
- 批量收藏地点到高德 App / 建高德收藏夹分组
- 生成可分享的地点地图（网页版 / My Maps / 高德导入文件）
- "把这份攻略/收藏夹变成地图"类需求

**Not for**: 行程规划（用 travel-planner）、机票火车票酒店查询、支付/订票操作。

**Output**: 在 `map-collections/<collection-id>/` 目录下生成数据与交付物：
`locations.json`（地点清单）→ `osm_geocoded_final.json`（定位）→
`vietnam-map.html` 式 Leaflet 地图 + `google-mymaps.csv` + 可选的高德 App 收藏灌入。

**Side effect**: 创建 `map-collections/` 子目录并写入 JSON/CSV/HTML/XLSX；
高德 App 收藏灌入会直接修改用户账号云端数据（需用户已扫码登录）。

---

## 核心能力

| 能力 | 路径 | 关键约束 |
|------|------|---------|
| 小红书合集/笔记读取 | redbook CLI（cookie 认证） | 私密合集见 refs/content-access.md 的聊天 token 路径 |
| 抖音分享链接读取 | Playwright 匿名访问视频页 | webfetch 会被 JS 盾拦截，必须真实浏览器 |
| 国内地点定位 | 高德 Web 服务 `place/text`（key 在 config） | 海外不可用（10002） |
| 海外地点定位 | Photon (photon.komoot.io) 国内可直连 | Nominatim 被干扰；必须做城市范围校验 |
| 高德 App 收藏灌入 | ditu.amap.com cloudSync 捕获-重放 | 详见 refs/amap-cloudsync.md，有严格字段要求 |
| 地图小程序导入 | 官方模板 xlsx（仅国内坐标） | 海外坐标 API/导入全链路被拒 |
| 网页地图交付 | Leaflet + 高德世界瓦片 + uri.amap.com 导航深链 | 国内直连、微信可直接分享 |

## 前置条件

1. **redbook CLI**：`npm i -g @lucasygu/redbook`，cookie 配置在
   `.opencode/skills/travel-planner/config.json`（与 travel-planner 共享，gitignored）。
   过期时用 Playwright 起 xiaohongshu.com 登录页扫码获取新 cookie（F12 复制亦可）。
2. **Playwright 浏览器**：用于抖音读取与高德登录/协议重放。若 playwright-mcp 报
   chrome 不存在：`npx playwright install chromium` 后建 junction
   `%LOCALAPPDATA%\Google\Chrome\Application` → ms-playwright 的 chrome-win 目录。
3. **高德 Web 服务 key**（国内定位用）：同 config.json 的 `amap_key`。
4. **Python 3.10+**（openpyxl 用于 Excel 生成）。

## 目录约定

```
map-collections/<collection-id>/     # 一个合集一个目录（如 xhs-board-6a52494f）
├── README.md                        # 合集说明与来源
├── locations.json                   # ★ 地点清单（提取产物，LLM 生成）
├── osm_geocoded_final.json          # ★ 最终定位数据（含精度标记）
├── notes_digest.json                # 笔记摘要（提取用）
├── note_list.json / board.json      # 笔记列表 / 合集元数据
├── amap_fav_data.json               # 高德收藏灌入数据快照
├── notes/                           # 笔记原始 JSON
├── <name>-map.html                  # 交付：Leaflet 网页地图
├── google-mymaps.csv                # 交付：My Maps 导入
├── amap-import-v3.xlsx              # 交付：地图小程序导入（国内）
├── data/                            # 中间产物（聊天dump、迭代定位数据）
├── captures/                        # API 协议捕获样本
├── artifacts/                       # 截图/失败回传（gitignored）
└── scripts/                         # 该合集专用脚本（硬编码修正表等）
```

skill 通用脚本在 `map-planner/scripts/`，全部支持 `--dir <collection目录>`（缺省取最新）。

## 工作流（六阶段）

### 阶段 1：内容获取

**小红书**：
1. `redbook board <url> --cookie-string ... --json` 拉合集列表（注意：私密合集会失败）
2. 逐篇 `redbook read <note_url_with_xsec_token>`（间隔 ≥3s，断点续跑）
3. **私密/共享专辑路径**（board API 拒绝非所有者时）：让所有者把笔记分享到与你账号的
   聊天 → 免签名直调 `GET https://edith.xiaohongshu.com/api/im/web/messages/history?chat_user_id=<uid>&last_id=0&start_id=0&limit=100`
   （带 cookie 即可）→ 从 ct=3 卡片的 `content.content.link` 提取 `xsec_token`
4. Windows 下调 redbook 必须 `node cli.js` 直调（`.cmd` 垫片会切坏 cookie 分号）

脚本：`read_notes.py --board-url <url> [--read|--read-only]`

**抖音**：分享短链 v.douyin.com/xxx → Playwright 逐条访问（匿名可看视频页）→
提取 document.title（含话题）、正文、AI 章节摘要（含店名）、"大家都在搜"提示。
批量访问分批 ≤5 条/次（MCP 超时），间隔 1.2s+。

### 阶段 2：地点提取（LLM）

`make_digest.py` 压缩笔记为摘要 → 人工/LLM 通读产出 `locations.json`：
```json
[{"display": "粉红教堂（新定教堂）", "query": "Tan Dinh Church",
  "city": "胡志明市", "category": "景点", "notes": ["来源笔记标题"],
  "address": "笔记中提到的地址", "fallback_query": "备用地标", "approx": false}]
```
- 中文 display + 英/越文 query（定位搜索用）+ category（景点/美食/按摩/住宿/购物/交通）
- 同地点多篇来源合并进 notes；无名摊位用 `approx:true` 挂靠地标

### 阶段 3：定位

- **国内**：`geocode_amap.py`（place/text，增量缓存，配额保护）
- **海外**：`osm_geocode_v2.py`（Photon + 城市坐标偏置 + bbox 过滤）
- **校验**：`validate_coords.py`（城市范围校验，拦截同名异城误配——必跑！）
- **排重**：`dup_analysis.py`（同名/同坐标堆叠分析）
- 误配修正：websearch 查权威地址 → Nominatim（webfetch 走平台网络可绕过本地干扰）精确定位
- ⚠️ **若后续要灌高德 App 收藏：同坐标堆叠点必须预先错开 5-30 米**（App 按墨卡托像素去重）

### 阶段 4：生成交付物

| 交付物 | 脚本 | 说明 |
|--------|------|------|
| Leaflet 网页地图 | `make_final_deliverables.py` | 高德瓦片国内直连 + 每点高德导航深链；同时产出 My Maps CSV |
| 地图小程序 Excel | `make_excel_v4.py` | 基于官方模板；**单元格必须是文本类型**；仅国内坐标可用 |
| 高德 App 收藏 | `make_fav_data.py` + 协议重放 | 见 refs/amap-cloudsync.md |

### 阶段 5：高德 App 收藏灌入（可选，海外也支持）

按 refs/amap-cloudsync.md 的协议与流程执行。核心步骤：
1. Playwright 登录 ditu.amap.com（高德 App 扫码，SSO）
2. 建 type:102 收藏夹分组
3. 批量创建 type:101 合法自定义点（**结构必须合规**，parent=分组id）
4. **让用户在手机上手动批量移动一次收尾**（App 自动转换不可靠）
5. 用户手机刷新验证

### 阶段 6：验证与交付

- 网页地图浏览器打开目检
- 高德 App 收藏核对数量与分组
- README 记录来源、统计、遗留事项

## 脚本清单（map-planner/scripts/）

| 脚本 | 功能 |
|------|------|
| `read_notes.py` | 小红书合集/笔记批量读取（断点续跑、风控保护） |
| `make_digest.py` | 笔记 JSON → 紧凑摘要（供 LLM 提取） |
| `geocode_amap.py` | 国内：高德 place/text 定位 |
| `osm_geocode_v2.py` | 海外：Photon 定位（增量落盘、城市偏置） |
| `validate_coords.py` | 城市坐标范围校验（防同名异城） |
| `dup_analysis.py` | 重复/堆叠分析 |
| `make_excel_v4.py` | 地图小程序导入 xlsx（官方模板 + 文本单元格） |
| `make_final_deliverables.py` | Leaflet HTML + My Maps CSV |
| `make_fav_data.py` | 高德 App 收藏灌入数据生成 |

## 常见错误与坑（速查）

| 症状 | 根因 | 解法 |
|------|------|------|
| redbook "Session expired" | web_session 过期（2-4周） | Playwright 扫码或 F12 更新 config.json |
| 合集读出 0 篇 + "该专辑还没收藏任何笔记" | 私密合集（board/info 的 privacy:1） | 走聊天分享 token 路径 |
| Nominatim SSL UNEXPECTED_EOF | 国内链路被干扰 | 用 Photon；精确地址查询用 webfetch 走平台网络 |
| 高德 place/text 搜海外返回国内结果 | 国内接口不覆盖海外 | osm_geocode_v2.py |
| 地图小程序导入"经纬度字段无效" | 单元格是数字类型 / 海外坐标 | 文本单元格 + 仅国内；海外走 App 收藏灌入 |
| App 收藏"地点已失效" | 记录是"POI样式+空poiid"畸形结构 | 用合法自定义点结构（见 refs） |
| 收藏夹只进了部分点 | App 按墨卡托像素去重，堆叠点每组只收 1 个 | 预先错开坐标 5-30 米 |
| App 管理页出现重影 | 外部多轮快速写入导致本地库分叉 | 云端清干净后退出账号重登；写入节奏放慢 |

## 相关参考

- `refs/amap-cloudsync.md` — 高德个人收藏云同步协议（字段表、公式、捕获-重放全流程）
- `refs/content-access.md` — 小红书/抖音内容获取路径与权限边界
- worklog（~/worklogs）：搜"高德 cloudSync"、"小红书 私密合集"可查完整排障记录
