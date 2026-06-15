# my-skills

OpenCode / AI Agent skills 仓库。存放自研 skill 及由其生成的产出物。

## 目录结构

```
my-skills/
├── skills-creator/       # Skill：生成规范 SKILL.md 脚手架
├── travel-planner/       # Skill：旅行规划，对接 MCP 生成可视化 HTML 行程
├── travel-plans/         # 产出物：每次旅行规划的 HTML + 数据
│   └── jeju-20260703/    #   济州岛 4天3晚 (2026.07.03-06)
├── scripts/
│   └── sync-pages.sh     # 将 travel-plans/ 同步到 gh-pages 分支
├── .opencode/            # [git-ignored] agent 运行时配置，symlink 指向顶层 skill
├── .github/workflows/    # CI：同步到 GitCode 镜像
└── init.sh               # 首次 clone 后运行，建立 .opencode/skills 软链接
```

## 快速开始

```bash
git clone <repo-url>
bash init.sh                         # 1. 创建 skill 软链接 + 写入 MCP 配置
opencode mcp auth nowah-travel       # 2. 一次性浏览器授权（首次必需）
```

**两条命令就够了：**
- `init.sh` 自动完成 symlink 和 MCP config 写入（幂等，可重复跑）
- `opencode mcp auth nowah-travel` 会弹出浏览器，完成 nowah OAuth 登录。只需一次性授权，token 会持久保存

> 💡 `init.sh` 运行结束时也会打印这条 OAuth 命令提醒你。如果已授权过，`init.sh` 会跳过提示。

## 当前包含的 Skill

| Skill | 说明 |
|-------|------|
| `skills-creator` | 生成规范 SKILL.md 脚手架，遵循 OpenCode 官方 spec |
| `travel-planner` | 旅行规划，对接 nowah-travel / 12306 MCP，产出可视化 HTML 行程 |

## 产出物

| 计划 | 说明 |
|------|------|
| `travel-plans/jeju-20260703` | [济州岛 4天3晚](https://stonechan00.github.io/my-skills/travel-plans/jeju-20260703/index.html) (2026.07.03–06) |

## 初始化做了什么

`init.sh` 做四件事，全部幂等（重复跑不会破坏任何东西）：

| 步骤 | 内容 | 幂等方式 |
|------|------|---------|
| 1. Skill 软链接 | `.opencode/skills/` 下为每个顶层 skill 建 symlink | 检查是否已存在+目标正确 |
| 2. MCP 配置 | 写入 `nowah-travel` + `12306` 到项目级 `opencode.jsonc` | JSON 深合并，值一致则跳过 |
| 3. OAuth 检查 | 检测 nowah 认证状态，未认证提示命令 | 仅检测，不修改任何文件 |
| 4. CLI 工具 | 检查 `redbook`/`npx` 是否可用 | 仅检测+提示安装命令 |

## MCP 服务器

| 场景 | MCP | 接入方式 | 说明 |
|------|-----|---------|------|
| 国际航班/酒店/POI | **nowah-travel** | 远程 HTTP + OAuth | 免费额度，需一次性授权 |
| 国内火车票 | **12306** | 本地 `npx -y 12306-mcp` | 零 key，开箱即用 |
| 小红书攻略 | **redbook CLI** | `npm i -g @lucasygu/redbook` | 可选，Chrome Cookie 认证 |

> ⚠️ `oauth` 字段必须写成 `"oauth": {}`（空对象触发自动发现），**不能**写成 `"oauth": true`（boolean），否则 opencode 会报 "Ignoring MCP config entry without type"。
