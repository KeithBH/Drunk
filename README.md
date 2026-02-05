# Drunk

项目拆分为三个子工程：

- `backend/`：REST API 服务
- `frontend/`：桌面端/通用前端页面
- `mobile-web/`：移动端 H5 页面（支持相机拍照上传）

## 1. 本地启动步骤

### 启动后端

```bash
cd backend
cp .env.example .env
npm install
npm run dev
```

后端默认地址：`http://localhost:4000`

### 启动前端

```bash
cd frontend
npm run dev
```

前端默认地址：`http://localhost:5173`

### 启动移动端 H5

```bash
cd mobile-web
python3 -m http.server 5174
```

移动端页面地址：`http://localhost:5174`

## 2. 环境变量说明

后端使用 `.env`：

- `PORT`：后端服务端口（默认 `4000`）
- `CORS_ORIGIN`：允许跨域来源（默认 `*`）
- `MAX_UPLOAD_SIZE_MB`：JSON 请求体大小限制（默认 `10`）
- `APP_NAME`：服务名称

示例见：`backend/.env.example`

## 3. 接口文档入口

- OpenAPI 文档：`backend/openapi.yaml`
- 主要接口：
  - `POST /api/uploads`
  - `POST /api/recognize`
  - `GET /api/stats`
  - `GET /api/profile/preferences`
  - `POST /api/share`

## 4. 页面说明

`frontend/pages/` 内包含：

- `upload.html`：上传页
- `result.html`：识别结果页
- `dashboard.html`：统计看板页
- `share.html`：好友分享页

`mobile-web/index.html` 使用 `input[type=file][capture=environment]` 支持移动端优先调用后置相机。
