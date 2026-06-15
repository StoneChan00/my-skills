---
name: travel-planner
description: >
  旅行规划 Skill：结合 MCP 服务器查询机票、火车票、酒店、景点，生成完整行程方案。
  支持国内出行（12306-mcp 本地部署）和国际旅行（nowah 远程 HTTP，35+ 工具，覆盖 300+ 航司）。
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

⚠️ **2026.06 MCP 真实可用性实测**

| 老 skill 提到的包 | 实际状态 | 替代方案 |
|------------------|---------|---------|
| `npm i trvl` | ❌ npm E404 已下架 | 用 nowah 远程 HTTP |
| `npm i nowah-mcp-server` | ❌ npm 包不存在 | 用 `https://claw.nowah.xyz/mcp` 远程 HTTP |
| `npm i @navifare/moltravel-mcp` | ❌ npm 包不存在 | 暂不可用 |
| `npm i 12306-mcp` | ✅ 可用 (v0.3.8) | 继续用 |
| `npm i travel-mcp` | ❌ 2026-06-06 下架 | 用 nowah |

## MCP 服务器快速参考（2026.06 实测可用）

根据用户需求选择对应 MCP 服务器（详见 `refs/mcp-servers.md`）：

| 场景 | 推荐 MCP | 接入方式 | 价格 |
|------|---------|---------|------|
| **国际航班/酒店/POI** | **nowah** | 远程 HTTP + OAuth | 免费额度 |
| **国内火车票** | **12306-mcp** | 本地 `npx -y 12306-mcp` | 零 key |
| **攻略/美食参考** | **redbook CLI** | `npm i -g @lucasygu/redbook` → bash 调用 | 零 key（Chrome Cookie） |
| **兜底方案** | webfetch + 官网 | 直接抓取 | 无需配置 |
| 国内酒店 | webfetch 携程/Booking | HTTP 抓取 | — |
| 签证/汇率/天气 | nowah 工具集 | `get_visa_requirements` 等 | 免费 |

**优先级规则**：
- 国内火车票 → 12306-mcp（本地）
- 国际航班/酒店 → nowah（远程）
- 攻略/美食灵感 → redbook CLI 搜索小红书真实帖子（可选，显著提升实用性）
- MCP 不可用 → webfetch + 携程/春秋/Booking/Agoda 官网抓取

## 接入配置（OpenCode 格式）

在 `~/.config/opencode/opencode.jsonc`（全局）或项目 `.opencode/opencode.jsonc` 添加：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "nowah-travel": {
      "type": "remote",
      "url": "https://claw.nowah.xyz/mcp",
      "oauth": {},      // 空对象 = 自动 OAuth 发现；不要写成 `true`（schema 不认）
      "timeout": 30000
    },
    "12306": {
      "type": "local",
      "command": ["npx", "-y", "12306-mcp"],
      "timeout": 30000
    }
  }
}
```

**OpenCode 命令行验证**：

```bash
opencode mcp list                    # 查看已配置
opencode mcp auth nowah-travel       # 首次 OAuth 认证（打开浏览器）
```

⚠️ 老 `mcpServers.command` / `mcpServers.args` 格式是 Claude Desktop 风格，**OpenCode 用的是 `mcp` 字段 + `type: local/remote` 二选一**，不要用错。

## 工作流程

### 1. 需求收集
- **输入**：用户自然语言（如"国庆想去成都玩 4 天"）
- **提取**：出发地、目的地、日期、天数、人数、预算、偏好（美食/自然/人文）
- **缺失信息**：主动追问，不要猜测关键参数

### 2. 数据查询（优先 MCP，降级到 webfetch）

**Step 1：检查 MCP 工具是否已加载**（通过 `tools` 命令或系统提示判断）
- 若 `search_flights` / `search_hotels` / `find_pois` 可见 → 走 2A
- 若不可见 → 走 2B（降级）

**2A. MCP 路径**（推荐）：
- **国际航班/酒店**：调用 nowah 的 `search_flights` / `search_hotels`
- **国内火车票**：调用 12306-mcp 的 `get-tickets`
- **POI 景点**：调用 nowah 的 `find_pois`
- **天气/签证/汇率**：调用 nowah 的 `get_weather` / `get_visa_requirements` / `convert_currency`

**2B. 降级路径**（MCP 不可用时）：
- **航班时刻**：`webfetch(https://flights.ctrip.com/international/Schedule/<from>-<to>.html)`
- **实时价格**：`webfetch` 春秋官网 / Trip.com / 吉祥官网
- **酒店价格**：`webfetch` Booking / Agoda / KAYAK
- **POI 攻略**：`websearch` 搜索 "X 地 3 天行程 2026"

**所有价格必须有来源标注**（MCP 实时 / 哪个官网抓取 / 攻略站估算），不要只写一个数字。

**2C. 小红书攻略搜索（行程灵感 + 美食参考）**：

用 `redbook` CLI 从小红书获取真实用户攻略，作为行程安排和美食推荐的参考来源。
**这不是必须的步骤**，但能显著提升行程方案的实用性和真实感。

前置检查：
```bash
# 检查 redbook 是否安装
which redbook || npm list -g @lucasygu/redbook
# 验证连接
redbook whoami --json
```
若未安装 → `npm install -g @lucasygu/redbook`，若连接失败 → 提示用户在 Chrome 登录 xiaohongshu.com。

搜索示例（全部加 `--json` 获取结构化数据）：
```bash
# 目的地行程攻略（按互动量排序，取最热门的）
redbook search "<目的地><天数>天攻略" --sort popular --json
# 例如: redbook search "成都3天攻略" --sort popular --json

# 美食推荐
redbook search "<目的地>必吃美食" --sort popular --json
# 例如: redbook search "成都必吃美食推荐" --sort popular --json

# 特定景点/餐厅的详细笔记
redbook read https://www.xiaohongshu.com/explore/<noteId>

# 笔记评论（看用户真实反馈、避坑信息）
redbook comments https://www.xiaohongshu.com/explore/<noteId> --json
```

**如何使用搜索结果**：
- 从热门笔记中提取：**具体餐厅名/景点名、推荐菜品、人均价格、避坑建议**
- 将提取的信息融入行程方案的 `activities` 和餐饮推荐中
- HTML 行程中的美食/景点旁标注 `📕 小红书参考` + 笔记链接，增强可信度
- ⚠️ 小红书价格是 UGC 内容，可能过时。标注时写 `小红书用户反馈（参考）`，不要当精确价格

**搜索间隔 ≥ 3s**，避免触发限流。每轮搜索取 top 3-5 条足够，不用翻页。

### 3. 生成旅行计划文件夹

基于 `assets/travel-plan-template.html` 模板，生成完整行程并写入磁盘：

**目录结构**：
```
travel-plans/<目的地拼音或英文>-<出发日期>/
├── index.html          # 主行程页面（可视化日程 + 预算图表）
├── data.json           # 结构化行程数据（供后续迭代）
└── README.md           # 简要说明（目的地/日期/人数/创建时间/价格来源）
```

**命名规则**：`travel-plans/chengdu-20261001/`（小写拼音/英文 + 出发日期 YYYYMMDD）

**index.html 内容**（基于模板填充）：
- 顶部概览卡片：目的地、日期范围、总预算、出行人数
- 逐日行程表：时间轴样式，上午/下午/晚上分时段，含景点图 + 餐厅
- 交通方案表：车次/航班对比，含价格、出发时间、时长 + **数据来源标注**
- 住宿推荐区：3 档（经济/舒适/豪华），**每家酒店必填**：
  - 💰 价格范围（标注旺季/淡季）
  - 📊 `price_source`（哪平台 + YYYY-MM-DD 抓取）
  - ⚠️ `caveats`（如"携程/飞猪搜不到"、"旺季提前 1 月预订"）
  - 🔗 至少 2 个平台跳转链接按钮（携程/Agoda/Booking/Trip.com 任一）
- 预算明细：CSS 柱状图（交通/住宿/餐饮/门票 分类汇总）
- 地图链接：每日景点的 Google Maps / 高德地图搜索链接
- 页脚：明确写出价格来源（MCP 实时 / 哪个官网抓取时间 / 估值）

**data.json 结构**：
```json
{
  "destination": "成都",
  "dates": ["2026-10-01", "2026-10-04"],
  "departure_city": "北京",
  "travelers": 2,
  "budget": {
    "total": 8000, "currency": "CNY",
    "price_source": "12306 MCP + Booking webfetch（YYYY-MM-DD 抓取）"
  },
  "days": [
    {
      "date": "2026-10-01",
      "activities": [
        { "time": "09:00", "type": "attraction", "name": "武侯祠", "cost": 50 }
      ]
    }
  ],
  "transport": [
    {
      "type": "train", "number": "G87", "price": 702,
      "price_source": "12306-mcp 实时",
      "booking_url": "https://kyfw.12306.cn/..."
    }
  ],
  "hotels": [
    {
      "tier": "comfort", "name": "全季酒店",
      "price_per_night_per_room": 380,
      "price_range": "¥350-420/晚（不同房型）",
      "price_source": "携程 实时，YYYY-MM-DD 抓取",
      "price_source_note": "7 月旺季 ¥420；淡季 ¥350",
      "caveats": ["旺季需提前 2 周预订", "Booking 价格不含 10% 服务费"],
      "booking_urls": {
        "携程": "https://hotels.ctrip.com/hotels/<id>.html",
        "Booking": "https://www.booking.com/hotel/...",
        "Agoda": "https://www.agoda.com/..."
      }
    }
  ]
}
```

⚠️ **酒店字段强制规范**（2026-06-13 修订）：
- 每家酒店**必须**包含 `price_source` 字段（写明来源 + YYYY-MM-DD 抓取日期）
- 每家酒店**必须**至少 2 个 `booking_urls`（携程/Booking/Agoda 任一），用户可直接点击验证
- 价格**不能用年度均值**：必须标注是"7 月旺季"还是"淡季"，因为旺季可能贵 50-75%
- 标注"携程/飞猪是否可搜到"：小型 Guesthouse / 民宿 在中国 OTA 上通常搜不到

### 4. 迭代优化
修改 `data.json` → 重新渲染 `index.html`。用户说"换个酒店"时只更新对应字段并重新生成。

## 国内 vs 国际策略

| 判断条件 | 策略 |
|---------|------|
| 出发地/目的地均在中国城市 | 12306-mcp（本地） + nowah `get_visa_requirements` 验证是否需签证 |
| 涉及境外目的地 | nowah 远程 MCP（`search_flights` / `search_hotels` / `find_pois`） |
| 中国出发 + 境外目的地 | nowah（国际段）+ 12306-mcp（国内段接驳） |
| MCP 都不可用 | webfetch 携程国际 / Trip.com / Booking / Agoda |

## Common Mistakes

| Mistake | Effect | Fix |
|---------|--------|-----|
| **用 `npx -y trvl` 安装** | E404 包已下架（2026.06） | 改用 nowah 远程 HTTP URL，见上方配置模板 |
| **用 `mcpServers` 字段（非 OpenCode）** | OpenCode 不识别 | 用 `mcp` 字段 + `type: local/remote` |
| **酒店价格用年度均值** | 价格严重偏差（旺季贵 50-75%），实际价格翻倍 | 必须抓 7 月旺季实时价，并明确标注"旺季 vs 淡季" |
| **不标注价格来源和抓取日期** | 用户无法验证，无法在携程/飞猪对比 | 每家酒店必附 `price_source` + `booking_urls` (≥2 家) + YYYY-MM-DD |
| **HTML 酒店价格不附平台跳转链接** | 用户要重新搜索才能验证价格 | 每家酒店至少 2 个平台按钮（携程/Booking/Agoda/Trip.com） |
| **Guesthouse 类小店标成"标准酒店"** | 用户上携程搜不到 | 加 caveat："这家是中国 OTA 不收录的小型民宿" |
| **用错汇率** | CNY→KRW≠USD→CNY，换算差 20% | 直接引用各平台显示的人民币/当地币种价格，避免二次换算 |
| 不查询 MCP 直接用 LLM 知识编造价格 | 价格过时/虚高，用户按假数据规划 | 所有价格必须来自 MCP 或标注来源的 webfetch |
| 价格只写数字不标来源 | 用户无法验证、无法追溯 | 每个价格旁附 `数据来源（YYYY-MM-DD 抓取）` |
| 忘记 12306 Cookie 有效期 | 连续查询被 12306 限流/封 IP | 查询间隔 ≥ 2s，遇限流提示用户稍候 |
| 同时加载多个 MCP 导致 context 爆炸 | Agent 上下文被工具描述占满 | 按需启用：在 opencode.json 用 `enabled: false` 临时关闭 |
| 猜测用户出发城市 | 方案不可执行 | 必须确认出发地，不要假设 |
| 假设 MCP 一定可用 | 用户环境 MCP 可能未配置 | 第 2 步先检查 tools 可见性再选路径 |
| 输出纯文字行程无预算 | 用户无法判断可行性 | 每个方案必须附预算明细表 + 来源 |
| HTML 用外部 CDN 依赖 | 离线/弱网下页面崩坏 | 模板必须全部内联，零外部依赖 |
| 目录名用中文 | 某些系统/工具路径解析异常 | 目录名只用小写英文/拼音 + 日期 |
| Windows redbook 报 `-101` 错误 | Chrome 127+ App-Bound Encryption 阻止 Cookie 读取 | 先关闭 Chrome 再运行 redbook，或用 `--cookie-string "a1=值; web_session=值"` 手动传入 |
| 把小红书 UGC 价格当精确价格 | 用户帖子可能几个月前发布，价格已变 | 标注 `📕 小红书参考`，不作为精确预算，让用户自行验证 |
| 频繁搜索 redbook 被限流 | 搜索间隔太短触发风控 | 搜索间隔 ≥ 3s，每轮取 top 3-5 条即够 |

## 中国旅行平台现状（2026.06）

- **飞猪 FlyAI**：AI 开放平台，支持 MCP Skill。API Key 需企业认证；个人可通过 OpenClaw 一键装 Skill（`clawhub install flyai`），额度有限。
- **携程商旅**：MCP 仅对企业开放（2026.4 上线），个人不可用。
- **携程个人**：网页端可通过 webfetch 抓取时刻表（`flights.ctrip.com/international/Schedule/<from>-<to>.html`），但**价格需要登录/JS 渲染**，webfetch 抓不到实时价。
- **同程旅行火车票 MCP**：可用，`npx` 启动，但稳定性不如 12306-mcp。
- **12306 开源方案**：`Joooook/12306-mcp` 最成熟（771⭐），推荐作为国内火车票首选。
- **春秋航空**：官网 `www.ch.com` 有时会有秒杀价（实际抓取到南京⇄济州 3.1 折 ¥309 起），但限特定日期。
- **Trip.com**（携程国际版）：webfetch 能抓到部分平均价格数据（如 HK$793 单程），但需二次计算汇率。
- **RollingGo**：个人开发者友好，机票+酒店 MCP，`rollinggo.store` 免费申请 Key。
- **小红书（攻略参考）**：无官方旅游攻略 API，但 UGC 内容极丰富。推荐用 `@lucasygu/redbook` CLI 搜索真实用户攻略帖（行程 + 美食），作为行程灵感的参考来源。Chrome Cookie 认证，零 API Key。备选方案 `openclaw-xhs` 提供完整 MCP 集成，但依赖链更重。

## Related skills (disambiguation)

- vs 纯 LLM 行程规划：本 skill 依赖 MCP + webfetch 提供实时数据，而非仅靠训练数据编方案
- vs `12306-mcp` 单独使用：本 skill 覆盖全旅行场景，12306-mcp 仅限国内火车票
- vs 地图/导航 skill：本 skill 生成行程方案，不负责实时导航或打车
- vs 浏览器自动化（playwright）：若 webfetch 抓不到价格（JS 渲染），可改用 playwright skill 直接登录抓取
