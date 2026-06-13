# MCP Servers 详细参考

## 国际旅行

### trvl — 综合国际旅行 MCP（推荐首选）
- **GitHub**: https://github.com/MikkoParkkola/trvl
- **特点**: 1 smart tool + 65 aliases + 22 providers，零 API Key
- **数据源**: Google Flights (protobuf) + Google Hotels + Trivago + Airbnb + Booking.com + Hostelworld + Kiwi + AFKLM Flying Blue + Ferryhopper
- **安装**: `npx -y trvl`
- **核心工具**:
  - `travel` — 智能路由器，根据意图分发
  - `search_flights` — 航班搜索
  - `search_hotels` — 酒店搜索
  - `plan_trip` — 航班+酒店并行搜索
  - `find_dates` — 灵活日期最低价
- **支持**: 机票/酒店/租车/火车/巴士/渡轮/价格追踪/天气/行李/贵宾室/目的地情报
- **Token 效率**: 1 tool = ~378 tokens（vs 65 tools = ~33K tokens）

### nowah-mcp-server — 全功能旅行 MCP
- **GitHub**: https://github.com/nowah-xyz/nowah-mcp-server
- **特点**: 远程 HTTP 端点，无需本地安装
- **数据规模**: 300+ 航司 / 全球酒店 / 116M+ POI
- **核心工具**:
  - `search_flights` — 航班搜索（多城市、灵活日期、舱位选择）
  - `search_hotels` — 酒店搜索
  - `find_pois` — 116M+ 全球 POI（餐厅/景点/活动）
  - `generate_itinerary` — AI 生成逐日行程
  - `track_flight` — 实时航班追踪
  - `check_visa` — 签证政策查询
  - `get_weather` — 天气预报
  - `convert_currency` — 货币转换
- **额外**: 支持预订/取消/行程管理全生命周期

### moltravel-mcp — 多 MCP 聚合器
- **GitHub**: https://github.com/navifare/moltravel-mcp
- **特点**: 聚合 Kiwi/Navifare/Peek MCP + 内置静态数据
- **21+ tools**: 航班搜索、比价、签证、机场/航司查询、旅行建议
- **零配置静态数据**: 机场(OurAirports) / 航司(OpenFlights) / 签证(Passport Index) / 国家信息

### travel-skill — 模块化旅行 MCP
- **GitHub**: https://github.com/JMMonte/travel-skill
- **特点**: flights + hotels + Airbnb + transit (44 城 GTFS)
- **架构**: flights(fli→Google Flights) / hotels(fast-hotels→Playwright) / Airbnb(requests→HTML) / transit(gtfs-mcp→Node.js)

---

## 国内出行

### 12306-mcp — 中国火车票查询（推荐）
- **GitHub**: https://github.com/Joooook/12306-mcp (771⭐)
- **安装**: `npx -y 12306-mcp`
- **工具**:
  - `get-tickets` — 余票查询（日期/出发站/到达站/车次筛选）
  - `get-interline-tickets` — 中转换乘查询
  - `get-train-route-stations` — 列车经停站
  - `get-stations-code-in-city` — 城市→车站列表
  - `get-station-code-of-city` — 城市→代表车站
  - `get-station-code-by-name` — 车站名→车站 ID

### mcp-server-12306 — Python 版 12306 MCP
- **GitHub**: https://github.com/drfccv/mcp-server-12306
- **安装**: `pip install mcp-server-12306` 或 Docker `docker run -d -p 8000:8000 drfccv/mcp-server-12306`
- **额外工具**: `query_ticket_price` (实时票价) / `query_transfer` (最优中转)
- **支持**: Streamable HTTP + STDIO 双模式

### 同程旅行火车票 MCP
- **接入**: `npx` 启动，遵循 MCP 规范
- **支持**: stdio / HTTP/SSE 传输
- **数据**: 同程旅行真实票务数据

---

## 飞猪/携程/去哪儿 — 中国 OTA 平台

### 飞猪 FlyAI
- **官网**: https://flyai.open.fliggy.com/
- **接入方式**: `clawhub install flyai` 或 `npx skills add alibaba-flyai/flyai-skill`
- **覆盖**: 机票/酒店/景区门票/度假套餐/用车
- **限制**: API Key 需企业认证；个人通过 OpenClaw 可用但额度低
- **传统 API**: https://open.alitrip.com/ （商家入驻制）

### 携程商旅 AI 开放平台
- **上线**: 2026 年 4 月 20 日
- **MCP 能力**: 酒店/机票/火车实时推荐 + 签证政策 + 差旅合规
- **适用**: 仅企业用户（需企业身份 + 商务对接）
- **个人开发者**: 不可用

### RollingGo（个人开发者首选）
- **官网**: rollinggo.store
- **接入**: 免费申请 Key，无最低消费
- **覆盖**: 机票 + 酒店
- **数据**: 实时

---

## 辅助 MCP

| MCP | 用途 | 安装 |
|-----|------|------|
| 高德地图 MCP | 景点标注/路线 | `@modelcontextprotocol/server-amap` |
| Google Maps MCP | 国际地图 | `@modelcontextprotocol/server-google-maps` |
| Open-Meteo | 免费天气 API | 直接 HTTP，无需 MCP |
