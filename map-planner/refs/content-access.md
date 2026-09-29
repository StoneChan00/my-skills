# 小红书 / 抖音内容获取路径与权限边界

## 小红书

### 认证
- **redbook CLI**（`npm i -g @lucasygu/redbook`）：cookie 认证，配置在
  `.opencode/skills/travel-planner/config.json` 的 `redbook_cookie`
  （格式 `a1=xxx; web_session=yyy`；web_session 有效期约 2-4 周）
- 验证：`redbook whoami --cookie-string "<cookie>" --json`
- **Windows 坑**：subprocess 调用必须 `node <APPDATA>/npm/node_modules/@lucasygu/redbook/dist/cli.js`
  直调——`.cmd` 垫片会把 cookie 里的分号当参数分隔符切坏
- **输出解析坑**：redbook 输出 = 前导提示行 + JSON + 尾随文本，必须用
  `json.JSONDecoder().raw_decode()` 从首个 `{` 解析，不能整串 `json.loads`

### cookie 失效后的获取方式
1. F12 手动复制（最简单）
2. Playwright 扫码：起浏览器 → xiaohongshu.com → 点"登录" → 截图二维码 →
   `Invoke-Item` 弹给用户扫 → 轮询登录态（注意 web_session 是 HttpOnly，
   `document.cookie` 读不到，要用 `page.context().cookies()` 或看页面 UI "我"/通知角标）

### 合集类型与读取路径

| 类型 | 判定 | 读取路径 |
|------|------|---------|
| 公开收藏合集 | board/info 返回 privacy:0 | `redbook board <url>` 直接拉 |
| 私密收藏合集 | privacy:1（非所有者 board/note API 返回 code:-1；页面显示"该专辑还没收藏任何笔记"是**假空状态**） | 见下方聊天 token 路径 |
| 共享专辑（协作） | 所有者邀请加入 | 同上（成员 web 端也拉不到列表——web 制度限制） |

### 私密合集的聊天 token 路径（核心套路）
1. 让**所有者**把笔记逐篇分享到与你账号的聊天（App 内"发送给"）
2. 免签名直调（带 cookie 的裸 fetch 即可，无需 x-s 签名）：
   `GET https://edith.xiaohongshu.com/api/im/web/messages/history?chat_user_id=<所有者uid>&last_id=0&start_id=0&limit=100`
3. ct=3 笔记卡片的 `content.content`（双重 JSON 嵌套）的 `link` 字段为
   `xhsdiscover://item/<note_id>?...&xsec_token=<token>&xsec_source=app_share`
4. 转成 `https://www.xiaohongshu.com/explore/<note_id>?xsec_token=<token>&xsec_source=app_share` 即可用 redbook 读取
5. 笔记详情含 `location` 字段（作者挂的位置标签）；desc 内常有地名/越南语地址

### 笔记读取要点
- 裸 note_id 访问会 404（"当前笔记暂时无法浏览"，error 300031）——**xsec_token 必需**
- 空 token 调 feed API 会触发验证码（risk control）

## 抖音

- 分享短链 `v.douyin.com/xxx` → 302 到 `douyin.com/video/<id>`，**匿名可看**
- webfetch 会被 JS 虚拟机反爬盾拦截（拿到的是 `_$jsvmprt` 混淆脚本）——**必须 Playwright 真实浏览器**
- 页面数据提取：`document.title`（含完整文案+话题）、body 文本（含 AI 章节摘要——
  常含店名/营业时间、"大家都在搜"联想词、评论区线索）
- 匿名直接访问 video URL 可能被弹到推荐流——先经短链跳转即可正常
- 批量访问：每批 ≤5 条（单次 MCP 调用超时限制），间隔 1.2s+，偶发"服务器出现问题"重试即可

## 通用风控注意
- 请求间隔 ≥3s（小红书）/ ≥1.2s（抖音）
- 断点续跑设计（已读文件跳过）防止中途风控后前功尽弃
