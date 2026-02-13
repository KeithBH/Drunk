# Drunk

Record your poison.

记录你的酒精摄入。

## Share API

This repository includes a Python HTTP service with sharing capabilities:

- `POST /api/share`: create a share link with share target, content scope, expiry, token, privacy settings, and source records.
- `GET /api/share/{token}`: fetch a privacy-safe share view (aggregated stats only by default).
- `POST /api/share/{token}/revoke?owner_id=<id>`: manually revoke a share link.

本仓库包含一个带分享能力的 Python HTTP 服务：

- `POST /api/share`：创建分享链接（包含分享对象、内容范围、过期时间、令牌、隐私设置与来源记录）。
- `GET /api/share/{token}`：获取隐私安全的分享视图（默认仅返回聚合统计）。
- `POST /api/share/{token}/revoke?owner_id=<id>`：手动撤销分享链接。

### Privacy defaults

- Share response hides raw records, image links, and notes.
- Brand/time details are hidden by default and can be toggled by `privacy.hide_brand_time`.
- Friend access can be toggled by `privacy.allow_friend_view`.

隐私默认策略：

- 分享响应会隐藏原始记录、图片链接与备注。
- 品牌/时间详情默认隐藏，可通过 `privacy.hide_brand_time` 切换。
- 朋友访问权限可通过 `privacy.allow_friend_view` 切换。

### Run

```bash
python app/main.py
```

运行：

```bash
python app/main.py
```

### Test

```bash
pytest -q
```

测试：

```bash
pytest -q
```

A lightweight backend service for recording alcohol consumption and generating analytics.

一个用于记录饮酒并生成分析的轻量后端服务。

## Data Model

Core tables (SQLite):

- `users`
- `drink_types`
- `drink_records`
- `shares`

核心表（SQLite）：

- `users`
- `drink_types`
- `drink_records`
- `shares`

`drink_records` includes required fields:

- `user_id`
- `drink_type`
- `abv`
- `volume_ml`
- `count`
- `drank_at`
- `source_image`
- `recognized_payload`

`drink_records` 包含必填字段：

- `user_id`
- `drink_type`
- `abv`
- `volume_ml`
- `count`
- `drank_at`
- `source_image`
- `recognized_payload`

Indexes for aggregation performance:

- `(user_id, drank_at)`
- `(user_id, drink_type)`

用于聚合性能的索引：

- `(user_id, drank_at)`
- `(user_id, drink_type)`

## API

### `GET /api/stats/consumption?range=week|month|year&user_id=1`

Returns:

- Total consumption (ml, standard drinks, grams of alcohol)
- Daily trend in the selected range

返回：

- 总摄入（毫升、标准杯、纯酒精克数）
- 选定范围内的每日趋势

### `GET /api/stats/favorites?user_id=1&top_n=5`

Returns top N most consumed drink type + brand combinations.

返回饮用最多的前 N 个“酒类 + 品牌”组合。

## Unit conversion

A centralized service layer computes:

- Volume in ml
- Standard drinks
- Pure alcohol grams

集中式服务层计算：

- 毫升体积
- 标准杯数
- 纯酒精克数

## Run

```bash
python3 app.py
```

运行：

```bash
python3 app.py
```

## Test

```bash
python3 -m unittest -v
```

测试：

```bash
python3 -m unittest -v
```

## Full-stack deployment (low-cost)

If you want both frontend and backend online with the lowest ongoing cost, use this split:

- Frontend: Cloudflare Pages (free)
- Backend API: Render Web Service (free tier)

全栈低成本部署建议：

如果希望以前后端最低持续成本上线，建议采用以下拆分：

- 前端：Cloudflare Pages（免费）
- 后端 API：Render Web Service（免费档）

### 1) Deploy frontend (Cloudflare Pages)

1. Push this repo to GitHub.
2. In Cloudflare Pages, create a new project from the repo.
3. Use these settings:
   - Root directory: `frontend`
   - Build command: *(empty)*
   - Output directory: `.`
4. Deploy and get your `*.pages.dev` domain.

1) 部署前端（Cloudflare Pages）

1. 将本仓库推送到 GitHub。
2. 在 Cloudflare Pages 中从该仓库创建新项目。
3. 使用以下设置：
   - 根目录：`frontend`
   - 构建命令：*(空)*
   - 输出目录：`.`
4. 部署并获得 `*.pages.dev` 域名。

### 2) Deploy backend (Render)

1. In Render, create a new **Web Service** from the same GitHub repo.
2. Select root directory `backend`.
3. Runtime: **Node**.
4. Start command: `npm start`.
5. Add env vars as needed:
   - `PORT` (Render will usually inject this)
   - `CORS_ORIGIN=https://<your-pages-domain>`
6. Deploy and copy the API base URL, e.g. `https://drunk-api.onrender.com`.

2) 部署后端（Render）

1. 在 Render 中用同一 GitHub 仓库创建 **Web Service**。
2. 选择根目录 `backend`。
3. 运行时：**Node**。
4. 启动命令：`npm start`。
5. 按需添加环境变量：
   - `PORT`（Render 通常会自动注入）
   - `CORS_ORIGIN=https://<your-pages-domain>`
6. 部署并复制 API 基址，例如 `https://drunk-api.onrender.com`。

### 3) Point frontend to backend

If frontend calls `/api/...` on same origin, add one of these:

- Cloudflare Pages redirect/proxy rules to your backend API domain, or
- update frontend requests to use absolute API base URL from environment/config.

3) 前端指向后端

如果前端用同源 `/api/...` 调用，可选其一：

- 在 Cloudflare Pages 配置重定向/代理规则指向后端 API 域名，或
- 将前端请求改为从环境变量/配置读取的绝对 API 基址。

### 4) Optional custom domain

- Bind frontend domain in Cloudflare Pages.
- Bind backend API subdomain (e.g. `api.example.com`) in Render.
- Keep HTTPS enabled on both sides.

4) 可选自定义域名

- 在 Cloudflare Pages 绑定前端域名。
- 在 Render 绑定后端 API 子域（如 `api.example.com`）。
- 前后端均保持 HTTPS。
