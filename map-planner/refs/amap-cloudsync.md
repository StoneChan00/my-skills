# 高德个人收藏 cloudSync 协议（捕获-重放手册）

> 2026-09-28/29 实测逆向，用于把任意坐标（含海外）批量灌入高德 App 个人收藏与收藏夹分组。
> 协议未公开，字段语义来自对照实验推断。

## 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `https://amap-pc-ssr.amap.com/ssr/api/cloudSync` | POST | 写入（增/改/删） |
| `https://amap-pc-ssr.amap.com/ssr/api/cloudSync?ver=&dltype=1X` | GET | 下载收藏点/分组（type 1xx） |
| `https://amap-pc-ssr.amap.com/ssr/api/cloudSync?ver=&dltype=3X` | GET | 下载路线/足迹（type 3xx） |

**请求头**（缺一不可）：
```
content-type: application/json
x-csrf-token: <cookie 里的 x-csrf-token 值>   # document.cookie 读取
x-adiu: <固定设备串，一次捕获长期复用>
```
凭据靠浏览器会话 cookie（ditu.amap.com 与 wia.amap.com 共享 SSO）。

**通用包裹结构**：
```json
{"data": [{"id": "<32hex>", "type": 101, "act": "c|u|d", "ts": 1790000000,
           "data": { ...记录体... }}],
 "ver": "<上次响应返回的版本号>"}
```
`ver` 链式传递：每次响应带新 ver，下一个请求用它。响应 `{"code":1,"done":1,"ver":"..."}` 即成功。

## 记录类型

| type | 含义 | 说明 |
|------|------|------|
| 101 | 收藏点（默认收藏夹） | 外部可创建 ✅ |
| 102 | 收藏夹分组 | 外部可创建 ✅（data: item_id/name/create_time/sort） |
| 103 | 收藏路线 | — |
| 110 | **App 的"收藏夹成员"表示** | ⚠️ 只能由 App 自己生成。外部伪造的 110 不被认作分组成员，且会造成 App 端重影 |
| 301-322 | 路线/足迹（dltype=3X） | 与分组无关 |

**分组成员关系是 App 侧私有状态**：不在 cloudSync 可见范围内。外部唯一可靠的入组方式：
`type:101 合法点 + parent=<分组id>` → **用户在手机上手动"移动到收藏夹"收尾**。

## 合法自定义点记录体（关键字段）

```json
{
  "item_id": "<32hex，与外层 id 一致>",
  "poiid": "",
  "name": "显示名", "address": "显示地址",
  "custom_name": "显示名",       // ← 必填！与 name 同值
  "custom_address": "显示地址",  // ← 必填！与 address 同值
  "type": "0",                   // 自定义点必须是 "0"，不是 POI 类型码
  "classification": "",
  "end_poi_extension": "1",
  "version": "1",
  "lon": 106.690642, "lat": 10.78836,
  "point_x": "<str>", "point_y": "<str>",   // 见下方公式，必须真实计算
  "x": <int>, "y": <int>,
  "parent": "<分组id 或 空>",
  "create_time": 1790000000,
  "entrance_list": [], "item_pictures": [], "naviPos": [],
  ...其余字段全部留空字符串...
}
```

**畸形结构会报"地点已失效"**：POI 样式（type:"110206"/classification:"8"）+ 空 poiid + 空 custom_name 的混合体，App 一校验即拒绝移动/分组。

## point_x / point_y 公式（Web Mercator 像素 @zoom20）

```
px = round((lon + 180) / 360 × 268435456)
py = round((1 - asinh(tan(lat × π/180)) / π) / 2 × 268435456)
```
用南京/上海真实样本反算验证过。海外（WGS-84 == GCJ-02，无偏移）直接代入。

## 删除

`act:"d"` + `data:{"item_id": <id>}`。删除后云端留无数据墓碑（act:"d"，App 不显示，计数会含）。

## 批量灌入标准流程（抄作业）

1. **Playwright 登录**：起浏览器 → `wia.amap.com` 扫码（高德 App）→ 导航 `ditu.amap.com/ssr/faves`（SSO 生效，能看到用户原有收藏即成功）
2. **捕获**（首次）：页面内搜索任意国内地点 → 详情面板点"收藏" → browser_network_request 抓 POST cloudSync 的完整请求体（记录 x-adiu）
3. **建分组**：`type:102, act:"c", data:{item_id:<新32hex>, name:"<分组名>", create_time, sort:0}`
4. **建点**：循环 `type:101, act:"c"`（合法自定义点结构 + parent=分组id），间隔 ≥220ms，ver 链式
   - **堆叠点预先错开**：App 转换时按 point_x/point_y 去重，同坐标每组只收 1 个
5. **手机收尾**：让用户在高德 App 里手动批量"移动到收藏夹"（一次多选操作）——App 自动转换不可靠
6. **验证**：`dltype=1X` 下载统计（按坐标范围过滤点数）；手机刷新核对

## 反面教训

- 外部直接伪造 type:110 → 不入组 + App 管理页重影（选择联动的同记录多次渲染）
- 多轮快速外部写入 → App 本地库分叉出残影；根治 = 云端清干净后**退出账号重登**
- 地图小程序（wia 的 createResource）对海外坐标返回 30001"此位置不支持标记"——与 cloudSync 是两套权限，勿混淆
- cloudSync 不校验坐标国内范围（海外 OK），是绕过"地图小程序仅国内"的正道

## 下载过滤技巧

`dltype=1X` 的 items 里按 `lat<18 && 102<lon<111` 过滤即得越南点（排除中国全境：
中国最南约北纬18.2）。其他国家换算边界即可。
