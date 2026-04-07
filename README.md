# LightInspector 城市光环境监测系统

一个适合大学生计算机设计大赛 / 毕业设计演示的前后端分离项目，用于完成城市夜间光环境样本的上传、分析、评级、地图展示和预警管理。

当前版本特性：

- 前端：Vue 3 + Vite + Element Plus
- 后端：FastAPI + SQLAlchemy + SQLite
- 图表：ECharts
- 地图：Leaflet
- 认证：支持注册、登录、登录态保持、退出登录
- AI：使用独立 `ai_service.py` mock，方便后续替换为真实模型服务
- 演示数据：默认生成湖南长沙范围样本点位

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
├─ start_backend.bat
├─ start_frontend.bat
├─ start_project.bat
└─ README.md
```

说明：

- `backend/uploads/`、`backend/light_inspector.db`、`frontend/node_modules/`、`backend/.venv/` 属于本地运行产物，不应提交到 Git。
- 仓库里保留的是源码、依赖清单和启动说明；拉取代码后可在本地重新安装依赖并自动生成运行数据。

## 已实现功能

- 登录 / 注册
- 首页大屏统计
- 上传检测任务
- 检测报告详情
- 历史记录查询
- 地图监测展示
- 预警列表与状态切换

## 启动方式

### 方式一：一键启动

可直接双击根目录下的脚本：

- `start_project.bat`：同时启动前后端
- `start_backend.bat`：只启动后端
- `start_frontend.bat`：只启动前端

### 方式二：手动启动

#### 1. 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端地址：

- `http://127.0.0.1:8000`
- 健康检查：`http://127.0.0.1:8000/api/health`

#### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：

- `http://127.0.0.1:5173`

## 首次运行说明

- 后端启动后会自动建表
- 会自动生成一批演示用种子数据
- 默认演示点位位于湖南长沙范围
- 首页和地图页会直接显示这些样本
- 首次进入系统需要先注册账号，再登录

## 程序入口

- 后端入口：[backend/app/main.py](D:/计设/lightInspector/backend/app/main.py)
- 前端入口：[frontend/src/main.js](D:/计设/lightInspector/frontend/src/main.js)
- 登录页：[frontend/src/views/Login.vue](D:/计设/lightInspector/frontend/src/views/Login.vue)
- 地图组件：[frontend/src/components/LeafletMap.vue](D:/计设/lightInspector/frontend/src/components/LeafletMap.vue)

## AI 接口替换说明

当前 AI 检测走统一服务层：

- [ai_service.py](D:/计设/lightInspector/backend/app/services/ai_service.py)

统一入口：

```python
analyze_images(east_image, south_image, west_image, north_image)
```

当前实现为 mock，但前后端已经按固定返回结构联通。后续如果你队友要接真实模型，建议只改这个服务层，不要改路由层和页面层。

可替换方式：

1. 在 `ai_service.py` 中通过 HTTP 调用外部模型服务
2. 在 `ai_service.py` 中直接接本地推理逻辑

## 其他可替换服务

- 地理信息服务：[geo_service.py](D:/计设/lightInspector/backend/app/services/geo_service.py)
- 卫星夜光服务：[satellite_service.py](D:/计设/lightInspector/backend/app/services/satellite_service.py)
- 生态脆弱度服务：[ecology_service.py](D:/计设/lightInspector/backend/app/services/ecology_service.py)
- 综合评分服务：[scoring_service.py](D:/计设/lightInspector/backend/app/services/scoring_service.py)

## 开发说明

- 前端展示中的四张样本图统一命名为“图片1 ~ 图片4”
- 后端上传字段仍然保留 `east / south / west / north`
- 地图默认中心点为长沙附近，优先使用中文底图
- 本地上传图片会保存到 `backend/uploads/`
- 本地数据库文件为 `backend/light_inspector.db`

## Git 注意事项

以下目录只应在本地存在，不应提交到仓库：

- `frontend/node_modules/`
- `backend/.venv/`
- `backend/uploads/`
- `backend/light_inspector.db`

这些目录已经在 `.gitignore` 中排除。它们不进 Git 不会影响别人运行，因为：

- 前端依赖可通过 `npm install` 重新安装
- 后端依赖可通过 `pip install -r requirements.txt` 重新安装
- 数据库和上传目录会在本地运行时自动生成
