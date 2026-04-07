# 城市光污染监测与智能评级系统

技术栈：

- 后端：FastAPI + SQLAlchemy + SQLite
- 前端：Vue3 + Vite + Element Plus
- 图表：ECharts
- 地图：Leaflet
- AI：Mock Service，可替换为真实模型接口

## 项目结构

```text
lightInspector/
├─ backend/
│  ├─ app/
│  │  ├─ core/
│  │  ├─ database/
│  │  ├─ models/
│  │  ├─ routers/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  ├─ utils/
│  │  └─ main.py
│  ├─ uploads/
│  ├─ light_inspector.db
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ api/
│  │  ├─ components/
│  │  ├─ layout/
│  │  ├─ router/
│  │  ├─ styles/
│  │  ├─ utils/
│  │  ├─ views/
│  │  ├─ App.vue
│  │  └─ main.js
│  ├─ index.html
│  ├─ package.json
│  └─ vite.config.js
└─ README.md
```

## 启动方式

### 一键启动

直接双击根目录下的：

- `start_project.bat`：同时启动前后端，并尝试自动打开浏览器
- `start_backend.bat`：只启动后端
- `start_frontend.bat`：只启动前端

首次启动时会自动安装依赖，因此会稍慢一些。

### 1. 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端默认地址：

- `http://127.0.0.1:8000`
- 健康检查：`http://127.0.0.1:8000/api/health`

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：

- `http://127.0.0.1:5173`

## 程序入口

- 后端入口：`backend/app/main.py`
- 前端入口：`frontend/src/main.js`
- 后端启动命令核心：`uvicorn app.main:app --reload`

## 已实现页面

- 首页大屏 Dashboard
- 上传检测页 TaskCreate
- 检测详情页 TaskDetail
- 历史记录页 TaskHistory
- 地图监测页 MapMonitor
- 预警列表页 WarningList

## AI 替换说明

当前 AI 检测走统一服务层：

- `backend/app/services/ai_service.py`

统一入口：

```python
analyze_images(east_image, south_image, west_image, north_image)
```

当前返回结构已经固定，前后端都依赖这层数据格式。因此后续接入真实模型时，建议只改这个文件内部实现，不要改路由层和页面层。

可替换方向：

1. 在 `ai_service.py` 内用 `requests` 调用你队友部署的模型 HTTP 接口
2. 在 `ai_service.py` 内直接调用本地推理代码

只要最终返回的数据结构保持一致，系统其他部分无需修改。

## 其他可替换服务

- 地理信息服务：`backend/app/services/geo_service.py`
- 卫星夜光服务：`backend/app/services/satellite_service.py`
- 生态脆弱度服务：`backend/app/services/ecology_service.py`
- 综合评分逻辑：`backend/app/services/scoring_service.py`

## 说明

- 项目启动后会自动生成一批演示用种子数据
- 上传检测会把图片保存到 `backend/uploads/`
- 当前数据库为本地 SQLite，文件为 `backend/light_inspector.db`
