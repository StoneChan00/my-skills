# MCP Servers 详细参考（2026.06 实测版）

> ⚠️ 本文档反映 **2026 年 6 月** 各 MCP 服务器的实际可用性状态。
> skill 中提到的老 npm 包（trvl / nowah-mcp-server / moltravel-mcp）在 npm 上均已 E404 下架，
> 请勿使用 `npx -y <包名>` 安装。下方以 ✅ / ❌ 标注。

---

## 国际旅行

### ✅ nowah-mcp-server — 全功能远程 MCP（推荐）
- **GitHub**: https://github.com/nowah-xyz/nowah-mcp-server
- **状态**: npm 包不存在 ❌，但 **远程 HTTP 端点可用** ✅
- **验证方式**：`Invoke-WebRequest https://claw.nowah.xyz/mcp` → 返回 `{"error":"Missing API key"}`（证明在线，MCP 协议拒绝裸 GET）
- **接入方式**: 远程 HTTP URL `https://claw.nowah.xyz/mcp` + OAuth 认证
- **数据规模**: 300+ 航司 / 全球酒店 / 116M+ POI
- **35+ 核心工具**:
  | 类别 | 工具 | 用途 |
  |------|------|------|
  | **Flights** | `search_flights`, `search_locations`, `get_offer`, `book_flight`, `get_booking_fees` | 航班搜索/报价/预订 |
  | **Hotels** | `search_hotels`, `get_hotel_quote`, `book_hotel` | 酒店搜索/报价/预订 |
  | **Trips** | `list_trips`, `get_trip`, `create_trip`, `update_trip`, `cancel_trip`, `get_trip_documents` | 行程管理 |
  | **Tracking** | `get_flight_info`, `get_booking_tracking`, `get_airport_delays` | 实时航班追踪 |
  | **Seatmaps** | `get_seat_info`, `get_seat_recommendations` | AI 选座推荐 |
  | **Order** | `get_cancellation_quote`, `confirm_cancellation`, `get_order_services`, `add_order_services`, `create_change_request`, `confirm_flight_change` | 订单全生命周期 |
  | **Payments** | `create_checkout_session`, `list_payment_methods`, `pay_with_saved_card`, `get_payment_status`, `manage_payment_method` | 支付 |
  | **Intelligence** | `get_visa_requirements`, `get_weather`, `convert_currency`, `get_safety_info` | 签证/天气/汇率/安全 |
  | **POIs** | `find_pois`, `generate_itinerary` | 116M+ 全球 POI + 行程生成 |
  | **Claims** | `check_claim_eligibility`, `file_claim`, `list_claims` | EU261 延误理赔 |
  | **Concierge** | `chat_with_agent` | AI 管家 |
  | **Meta** | `get_usage_stats`, `get_server_info` | 用量查询 |
- **OpenCode 配置示例**:
  ```json
  {
    "mcp": {
      "nowah-travel": {
        "type": "remote",
        "url": "https://claw.nowah.xyz/mcp",
        "oauth": {},
        "timeout": 30000
      }
    }
  }
  ```
- **首次使用**: `opencode mcp auth nowah-travel` 浏览器登录
- **免费额度**: 注册后每月有免费查询（付费版 dash.nowah.xyz）

---

### ❌ trvl — 综合国际旅行（**npm 包已下架，2026.06 E404**）
- **GitHub**: https://github.com/MikkoParkkola/trvl （仓库还在）
- **历史特点**: 1 smart tool + 65 aliases + 22 providers，零 API Key
- **数据源**: Google Flights (protobuf) + Google Hotels + Trivago + Airbnb + Booking.com + Hostelworld + Kiwi + AFKLM Flying Blue + Ferryhopper
- **实际状态**:
  ```bash
  $ npm view trvl
  Error 404: Unpublished on 2026-06-xx
  ```
- **替代方案**: 改用 **nowah 远程 MCP**
- **如果仓库恢复了新版本**：需重新测试 npm 是否可用

---

### ❌ moltravel-mcp — 多 MCP 聚合器（**npm 包不存在**）
- **GitHub**: https://github.com/navifare/moltravel-mcp
- **历史特点**: 21+ tools，聚合 Kiwi/Navifare/Peek MCP，零配置静态数据（OurAirports/OpenFlights/Passport Index）
- **实际状态**: npm 上完全不存在 `@navifare/moltravel-mcp`，E404
- **替代方案**: 改用 nowah + 本地 static data fallback

---

### ❓ travel-skill — 模块化旅行 MCP（**状态待确认**）
- **GitHub**: https://github.com/JMMonte/travel-skill
- **历史特点**: flights + hotels + Airbnb + transit（44 城 GTFS）
- **架构**: flights(fli→Google Flights) / hotels(fast-hotels→Playwright) / Airbnb(requests→HTML) / transit(gtfs-mcp→Node.js)
- **实际状态**: 2026.06 未实测，使用前请先 `npm view travel-skill` 验证

---

## 国内出行

### ✅ 12306-mcp — 中国火车票查询（**强烈推荐**）
- **GitHub**: https://github.com/Joooook/12306-mcp (771⭐)
- **npm 包**: `12306-mcp` @ v0.3.8 ✅ 可用
- **安装**: `npx -y 12306-mcp`（首次会自动下载）
- **工具**:
  - `get-tickets` — 余票查询（日期/出发站/到达站/车次筛选）
  - `get-interline-tickets` — 中转换乘查询
  - `get-train-route-stations` — 列车经停站
  - `get-stations-code-in-city` — 城市→车站列表
  - `get-station-code-of-city` — 城市→代表车站
  - `get-station-code-by-name` — 车站名→车站 ID
- **OpenCode 配置示例**:
  ```json
  {
    "mcp": {
      "12306": {
        "type": "local",
        "command": ["npx", "-y", "12306-mcp"],
        "enabled": true,
        "timeout": 30000
      }
    }
  }
  ```
- **注意**: 12306 Cookie 有效期 30 分钟，连续查询间隔 ≥ 2s，避免限流

### ✅ mcp-server-12306 — Python 版 12306 MCP（**Docker 部署友好**）
- **GitHub**: https://github.com/drfccv/mcp-server-12306
- **特点**: Streamable HTTP + STDIO 双模式
- **安装选项**:
  1. `pip install mcp-server-12306`
  2. Docker: `docker run -d -p 8000:8000 drfccv/mcp-server-12306`
- **额外工具**: `query_ticket_price`（实时票价）/ `query_transfer`（最优中转）
- **OpenCode Docker 配置示例**:
  ```json
  {
    "mcp": {
      "12306": {
        "type": "remote",
        "url": "http://localhost:8000/mcp",
        "enabled": true
      }
    }
  }
  ```

### 同程旅行火车票 MCP（**可用但不如 12306-mcp 成熟**）
- **接入**: `npx` 启动，遵循 MCP 规范
- **支持**: stdio / HTTP/SSE 传输
- **数据**: 同程旅行真实票务数据
- **建议**: 优先用 12306-mcp

---

## 飞猪/携程/去哪儿 — 中国 OTA 平台（MCP 受限）

### 飞猪 FlyAI
- **官网**: https://flyai.open.fliggy.com/
- **接入方式**: `clawhub install flyai` 或 `npx skills add alibaba-flyai/flyai-skill`
- **覆盖**: 机票/酒店/景区门票/度假套餐/用车
- **限制**: API Key 需企业认证；个人通过 OpenClaw 可用但额度低
- **传统 API**: https://open.alitrip.com/（商家入驻制）

### 携程商旅 AI 开放平台
- **上线**: 2026 年 4 月 20 日
- **MCP 能力**: 酒店/机票/火车实时推荐 + 签证政策 + 差旅合规
- **适用**: **仅企业用户**（需企业身份 + 商务对接）
- **个人开发者**: ❌ 不可用

### 携程个人端抓取（webfetch 可用，但部分需 JS）
- **时刻表**: `webfetch https://flights.ctrip.com/international/Schedule/<from>-<to>.html` ✅ 可抓
- **实时价格**: 需登录 JS 渲染，webfetch 抓不到精确数值
- **建议**: 价格用 Trip.com 或航司官网

### RollingGo（个人开发者友好，**需 API Key**）
- **官网**: rollinggo.store
- **接入**: 免费申请 Key，无最低消费
- **覆盖**: 机票 + 酒店
- **数据**: 实时
- **使用**: 通过 HTTP 调用，不是 MCP

---

## 小红书攻略参考（CLI，非 MCP）

### ✅ @lucasygu/redbook — 小红书 CLI（**旅游推荐首选**）
- **GitHub**: https://github.com/lucasygu/redbook
- **npm 包**: `@lucasygu/redbook` ✅ 可用
- **安装**: `npm install -g @lucasygu/redbook`（需 Node.js >= 22）
- **认证**: Chrome 浏览器 Cookie（先登录 xiaohongshu.com），无需 API Key
- **验证**: `redbook whoami`
- **定位**: 为 AI Agent 设计的 CLI 工具，已内置 Claude Code / OpenClaw SKILL.md
- **旅游场景命令**:
  ```bash
  # 搜索目的地攻略（按互动量排序）
  redbook search "成都3天攻略" --sort popular --json

  # 搜索美食推荐
  redbook search "成都必吃美食推荐" --sort popular --json

  # 阅读某篇高赞笔记全文
  redbook read https://www.xiaohongshu.com/explore/<noteId>

  # 获取笔记评论（看用户真实反馈）
  redbook comments <url> --all --json

  # 搜索话题标签（了解热门话题）
  redbook topics "日本自由行"
  ```
- **通用选项**: `--json`（机器可读）、`--sort general|popular|latest`、`--type all|video|image`
- **Windows 注意**:
  - Chrome 127+ 使用 App-Bound Encryption，需**先关闭 Chrome** 再运行 redbook（CLI 自动启动 headless 读取 Cookie）
  - 如果仍失败，用 `--cookie-string "a1=值; web_session=值"` 手动传入（从 Chrome F12 → Application → Cookies 复制）
- **限流**: 搜索间隔建议 ≥ 3s，避免频繁调用
- **输出**: `--json` 返回结构化数组，含标题、正文、互动数据（点赞/评论/收藏数）、图片 URL 等

### ❓ openclaw-xhs — 小红书 MCP 封装（功能更全但依赖重于 redbook）
- **GitHub**: https://github.com/zhiyingxia/openclaw-xhs
- **特点**: 封装 `xiaohongshu-mcp` 二进制为 MCP tools（search_feeds / list_feeds / get_feed_detail / user_profile 等）
- **MCP tools**:
  | 工具 | 用途 |
  |------|------|
  | `search_feeds` | 搜索笔记 |
  | `list_feeds` | 首页推荐 |
  | `get_feed_detail` | 笔记详情 + 评论 |
  | `user_profile` | 用户信息 |
  | `like_feed` / `favorite_feed` | 点赞/收藏 |
- **安装步骤**:
  1. 从仓库下载 `xiaohongshu-mcp` 二进制
  2. 安装 openclaw-xhs 脚本
  3. 启动 MCP server → `http://localhost:18060/mcp`
- **OpenCode 配置**:
  ```json
  {
    "mcp": {
      "xiaohongshu": {
        "type": "remote",
        "url": "http://localhost:18060/mcp",
        "enabled": true,
        "timeout": 30000
      }
    }
  }
  ```
- **建议**: 依赖链较重，轻量搜索场景优先用 redbook CLI

### xhs-cli（不推荐，与 redbook 功能重叠）
- **GitHub**: https://github.com/hammershock/xhs-cli
- **类型**: Python CLI（pip 安装），4 个依赖
- **不推荐原因**: 与 redbook 功能高度重叠，且需 Python 环境 + pip 安装，不如 redbook 的 npm 一键安装方便

---

## 辅助 MCP

| MCP | 用途 | OpenCode 配置 | 备注 |
|-----|------|--------------|------|
| ✅ 高德地图 MCP | 景点标注/路线 | `"type":"local","command":["npx","-y","@modelcontextprotocol/server-amap"]` | 需 AMAP_MAPS_API_KEY |
| ✅ Google Maps MCP | 国际地图 | `"type":"local","command":["npx","-y","@modelcontextprotocol/server-google-maps"]` | 需 GOOG_API_KEY |
| ✅ Open-Meteo | **免费天气 API** | **直接用 HTTP，无需 MCP** | `webfetch https://api.open-meteo.com/v1/forecast?latitude=33.5&longitude=126.5&daily=temperature_2m_max` |

### webfetch 兜底数据源（MCP 不可用时）

```
航班时刻:  https://flights.ctrip.com/international/Schedule/<from>-<to>.html
航班价格:  https://hk.trip.com/flights/city-<from>-airport-<to>/
机票秒杀:  https://www.ch.com （春秋航空秒杀价有时低至 3 折）
酒店价格:  https://www.booking.com/city/<city>.html  (KAYAK/momondo 数据更透明)
攻略路线:  websearch "<目的地> 3 天行程 2026" 抓取 Trip.com/马蜂窝 攻略文章
景点门票:  websearch "<景点名> 门票 2026"
```

---

## OpenCode MCP 配置语法速查

**关键点**：OpenCode 用 `mcp` 字段（不是 `mcpServers`），通过 `type: local | remote` 二选一。

### 本地 MCP（本地启动 npm/Node 进程）
```json
{
  "mcp": {
    "my-local": {
      "type": "local",
      "command": ["npx", "-y", "<pkg>"],
      "enabled": true,
      "environment": { "MY_KEY": "value" },
      "timeout": 30000
    }
  }
}
```

### 远程 MCP（HTTP 端点）
```json
{
  "mcp": {
    "my-remote": {
      "type": "remote",
      "url": "https://example.com/mcp",
      "headers": { "Authorization": "Bearer xxx" },
      "oauth": {}
    }
  }
}
```

### 命令行管理
```bash
opencode mcp list                    # 查看已配置
opencode mcp add                     # GUI 添加
opencode mcp auth <name>             # OAuth 认证
opencode mcp logout <name>           # 登出
opencode mcp debug <name>            # 调试
```

---

## 验证 MCP 是否可访问的 Checklist

| 服务器 | 验证命令 | 期望结果 |
|--------|---------|---------|
| nowah | `Invoke-WebRequest -Uri "https://claw.nowah.xyz/mcp"` | `MISSING_API_KEY`（说明在线，MCP 协议拒绝裸 GET） |
| 12306-mcp | `npm view 12306-mcp` | 显示版本号（v0.3.8） |
| 高德地图 MCP | `npm view @modelcontextprotocol/server-amap` | 显示版本号 |
| Google Maps MCP | `npm view @modelcontextprotocol/server-google-maps` | 显示版本号 |
| ❌ trvl | `npm view trvl` | `Error 404: Unpublished` |
| ❌ moltravel | `npm view @navifare/moltravel-mcp` | `Error 404: Not Found` |
| ✅ redbook CLI | `npm view @lucasygu/redbook` | 显示版本号（需 Node >= 22） |
| ✅ redbook 连接 | `redbook whoami` | 显示用户名（需 Chrome 已登录小红书） |
