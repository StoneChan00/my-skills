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
bash init.sh              # 创建 .opencode/skills/ 软链接
```

`init.sh` 做的事很简单：在 `.opencode/skills/` 下为每个顶层 skill 目录建一条 symlink，让 OpenCode agent 能发现它们，同时避免运行时文件进入 git。

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

| 内容 | 说明 |
|------|------|
| `init.sh` | 在 `.opencode/skills/` 下为每个顶层 skill 建软链接，让 agent 能发现它们 |
| MCP 服务器 | nowah-travel（国际机酒）+ 12306（国内火车）已在全局 `opencode.json` 注册 |
| GitHub Pages 同步 | `scripts/sync-pages.sh` 将 `travel-plans/` 推送到 `gh-pages` 分支供在线访问 |
