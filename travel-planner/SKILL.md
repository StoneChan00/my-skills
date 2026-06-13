---
name: travel-planner
description: >
  旅行规划 Skill：结合 MCP 服务器查询机票、火车票、酒店、景点，生成完整行程方案。
  支持国内出行（12306 火车票 + 高德地图）和国际旅行（Google Flights/Hotels/Airbnb，零 API Key）。
  Use when: 用户提出旅行规划、行程安排、机票/火车票查询、酒店预订推荐、目的地攻略，
  或需要接入 travel MCP server 获取实时出行数据。
  Not for: 直接执行支付/订票操作（仅查询和规划）、实时导航/打车、签证代办（仅提供查询）。
  Output: 在 `travel-plans/<目的地>-<日期>/` 目录下生成可视化 HTML 行程方案
  （含交互式日程表 + 预算图表 + 地图链接），可直接浏览器打开。
  Side effect: 创建 `travel-plans/` 目录并写入 HTML/CSS/JSON 文件。
---

# Travel Planner

将 LLM 的行程规划能力与实时出行数据结合：通过 MCP 服务器获取机票/火车票/酒店/POI 真实数据，
生成可浏览器打开的 **可视化 HTML 行程方案**。

## MCP 服务器快速参考

根据用户需求选择对应 MCP 服务器（详见 `refs/mcp-servers.md`）：

| 场景 | 推荐 MCP | API Key | GitHub |
|------|---------|---------|--------|
| 综合国际旅行 | **trvl** | 零 key | MikkoParkkola/trvl |
| 国内火车票 | **12306-mcp** | 零 key | Joooook/12306-mcp (771⭐) |
| 全功能旅行助手 | **nowah** | 远程 HTTP | nowah-xyz/nowah-mcp-server |
| 航班+酒店+Airbnb+公交 | **travel-skill** | 无 | JMMonte/travel-skill |
| 聚合多 MCP | **moltravel** | 零配置静态数据 | navifare/moltravel-mcp |

**优先级规则**：国内火车票 → 12306-mcp；国际综合 → trvl；需要 POI/签证/天气 → nowah。

## 接入配置模板

在 `opencode.json` 或 MCP 客户端配置中声明（详见 `refs/mcp-config-examples.json`）：

```json
{
  "mcpServers": {
    "12306": {
      "command": "npx",
      "args": ["-y", "12306-mcp"]
    },
    "trvl": {
      "command": "npx",
      "args": ["-y", "trvl"]
    }
  }
}
```

## 工作流程

### 1. 需求收集
- **输入**：用户自然语言（如"国庆想去成都玩 4 天"）
- **提取**：出发地、目的地、日期、天数、人数、预算、偏好（美食/自然/人文）
- **缺失信息**：主动追问，不要猜测关键参数

### 2. 数据查询（并行调用 MCP）
- **交通**：12306-mcp 查火车票 / trvl 搜国际航班
- **住宿**：trvl 搜酒店 / nowah 搜全球酒店
- **景点**：nowah `find_pois` / 高德地图 MCP
- **天气**：nowah `get_weather_forecast`

### 3. 生成旅行计划文件夹

基于 `assets/travel-plan-template.html` 模板，生成完整行程并写入磁盘：

**目录结构**：
```
travel-plans/<目的地拼音或英文>-<出发日期>/
├── index.html          # 主行程页面（可视化日程 + 预算图表）
├── data.json           # 结构化行程数据（供后续迭代）
└── README.md           # 简要说明（目的地/日期/人数/创建时间）
```

**命名规则**：`travel-plans/chengdu-20261001/`（小写拼音/英文 + 出发日期 YYYYMMDD）

**index.html 内容**（基于模板填充）：
- 顶部概览卡片：目的地、日期范围、总预算、出行人数
- 逐日行程表：时间轴样式，上午/下午/晚上分时段，含景点图 + 餐厅
- 交通方案表：车次/航班对比，含价格、出发时间、时长
- 住宿推荐区：3 档（经济/舒适/豪华），含图片、评分、价格
- 预算明细：CSS 柱状图（交通/住宿/餐饮/门票 分类汇总）
- 地图链接：每日景点的 Google Maps / 高德地图搜索链接

**data.json 结构**：
```json
{
  "destination": "成都",
  "dates": ["2026-10-01", "2026-10-04"],
  "travelers": 2,
  "budget": { "total": 8000, "currency": "CNY" },
  "days": [
    {
      "date": "2026-10-01",
      "activities": [
        { "time": "09:00", "type": "attraction", "name": "武侯祠", "cost": 50 }
      ]
    }
  ],
  "transport": [{ "type": "train", "number": "G87", "price": 702 }],
  "hotels": [{ "tier": "comfort", "name": "全季酒店", "price": 380 }]
}
```

### 4. 迭代优化
修改 `data.json` → 重新渲染 `index.html`。用户说"换个酒店"时只更新对应字段并重新生成。

## 国内 vs 国际策略

| 判断条件 | 策略 |
|---------|------|
| 出发地/目的地均在中国城市 | 优先 12306-mcp + 国内酒店搜索 |
| 涉及境外目的地 | 使用 trvl（Google Flights）+ nowah（签证/POI） |
| 中国出发 + 境外目的地 | 国际航班用 trvl，国内段用 12306-mcp |

## Common Mistakes

| Mistake | Effect | Fix |
|---------|--------|-----|
| 不查询 MCP 直接用 LLM 知识编造价格 | 价格过时/虚高，用户按假数据规划 | 所有价格数据必须来自 MCP 实时查询 |
| 忘记 12306 Cookie 有效期 | 连续查询被 12306 限流/封 IP | 查询间隔 ≥ 2s，遇限流提示用户稍候 |
| 同时加载多个 MCP 导致 context 爆炸 | Agent 上下文被工具描述占满 | 按需加载：仅加载当前查询需要的 MCP |
| 猜测用户出发城市 | 方案不可执行 | 必须确认出发地，不要假设 |
| trvl 搜不到小众航线 | 遗漏廉价航空选项 | 补充 nowah（300+ 航司）交叉验证 |
| 输出纯文字行程无预算 | 用户无法判断可行性 | 每个方案必须附预算明细表 |
| HTML 用外部 CDN 依赖 | 离线/弱网下页面崩坏 | 模板必须全部内联，零外部依赖 |
| 目录名用中文 | 某些系统/工具路径解析异常 | 目录名只用小写英文/拼音 + 日期 |

## 中国旅行平台现状（2026.6）

- **飞猪 FlyAI**：AI 开放平台，支持 MCP Skill。API Key 需企业认证；个人可通过 OpenClaw 一键装 Skill（`clawhub install flyai`），额度有限。
- **携程商旅**：MCP 仅对企业开放（2026.4 上线），个人不可用。
- **同程旅行**：火车票 MCP Server 可用，`npx` 启动。
- **12306 开源方案**：`Joooook/12306-mcp` 最成熟（771⭐），推荐作为国内火车票首选。
- **RollingGo**：个人开发者友好，机票+酒店 MCP，`rollinggo.store` 免费申请 Key。

## Related skills (disambiguation)

- vs 纯 LLM 行程规划：本 skill 依赖 MCP 提供实时数据，而非仅靠训练数据编方案
- vs `12306-mcp` 单独使用：本 skill 覆盖全旅行场景，12306-mcp 仅限国内火车票
- vs 地图/导航 skill：本 skill 生成行程方案，不负责实时导航或打车
