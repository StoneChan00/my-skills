# Travel Planner

将 LLM 的行程规划能力与实时出行数据结合：通过 MCP 服务器获取机票/火车票/酒店/POI 真实数据，
生成可浏览器打开的 **可视化 HTML 行程方案**。

## 小红书攻略（redbook）可选配置

本 skill 可通过 `redbook` CLI 搜索小红书真实用户攻略，大幅提升行程实用性。**非必须**，不配置也能用（降级到 websearch）。

### 快速配置

```bash
bash init.sh --cookie
```

交互式输入 `a1` 和 `web_session` 两个 cookie 值，自动写入 `.opencode/skills/travel-planner/config.json`。

### 手动配置

创建 `.opencode/skills/travel-planner/config.json`：

```json
{
  "redbook_cookie": "a1=你的a1值; web_session=你的web_session值",
  "_note": "Cookie 有效期: a1 约6-12月, web_session 约2-4周。过期后运行 bash init.sh --cookie 更新。",
  "_updated": "YYYY-MM-DD"
}
```

**获取 cookie**（Chrome / Edge 通用）：
1. 打开浏览器，访问 `xiaohongshu.com` 并登录
2. F12 → Application（Chrome）或 应用程序（Edge）→ Cookies → `xiaohongshu.com`
3. 复制 `a1` 和 `web_session` 的值

### Cookie 过期处理

| 现象 | 原因 | 解决 |
|------|------|------|
| `redbook whoami` 报错/返回空 | `web_session` 过期（约 2-4 周） | 重新 `bash init.sh --cookie` |
| `redbook whoami` 正常但搜索报错 | Cookie 完整但被风控 | 等 5 分钟后重试 |

`config.json` 已被 `.gitignore` 排除（位于 `.opencode/` 目录下），**不会提交到 git**。

### 前置：redbook CLI 安装

```bash
npm install -g @lucasygu/redbook
```

⚠️ Windows 上 Chrome 127+ 因 App-Bound Encryption 可能无法自动读取 cookie，`--cookie-string` 手动传入可绕过此问题（见上方配置步骤）。

## 运行示例

配置好 cookie 后，直接让 agent 规划行程即可，skill 会自动读取 `config.json` 加载 cookie。

```
帮我规划 5 天日本大阪行程，参考小红书攻略
```
