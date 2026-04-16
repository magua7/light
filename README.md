# 净光物联城市光污染多模态感知监测与智能评级系统

一个面向真实业务场景的前后端分离项目，用于完成城市夜间光污染样本的上传、分析、评级、地图展示与预警管理。

## 项目特性

- 前端：Vue 3 + Vite + Element Plus
- 后端：FastAPI + SQLAlchemy + SQLite
- 图表：ECharts
- 地图：Leaflet
- 认证：支持注册、登录、登录态保持与退出登录
- AI：通过独立 `ai_service.py` 接入真实模型分析能力

## 项目结构

```text
lightInspector/
├─ backend/
│  ├─ app/
│  ├─ scripts/
│  │  └─ bootstrap_backend.py
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  ├─ package.json
│  └─ vite.config.js
├─ start_backend.bat
├─ start_frontend.bat
├─ start_project.bat
└─ README.md
```

## 环境要求

- Windows 10/11
- Python 3.10 或更高版本
- Node.js LTS
- 请确保 `python` 和 `npm` 已加入 PATH

## 推荐启动方式

### Windows 图形方式

可直接双击根目录脚本：

- `start_project.bat`：同时启动前后端
- `start_backend.bat`：只启动后端
- `start_frontend.bat`：只启动前端

其中：

- `start_backend.bat` 会调用 `backend/scripts/bootstrap_backend.py`
- 启动器会自动检查 Python 版本、准备虚拟环境、安装依赖并启动 FastAPI
- 如果 `.venv` 已损坏或来自别的机器，会自动重建
- 如果 `.venv` 被占用无法删除，会自动回退到 `.venv_bootstrap`
- pip 默认源失败后，会自动尝试清华镜像
- `start_frontend.bat` 会自动检查 `node` / `npm`
- `node_modules` 不存在或不完整时，会自动安装依赖并启动 Vite

### 命令行方式

后端：

```bash
cd backend
python scripts/bootstrap_backend.py
```

前端：

```bash
cd frontend
npm install
npm run dev
```

访问地址：

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8000`
- 健康检查：`http://127.0.0.1:8000/api/health`

## 已实现功能

- 登录 / 注册
- 首页大屏统计
- 上传检测任务
- 检测报告详情
- 历史记录查询
- 地图监测展示
- 预警列表与状态处理

## 首次运行说明

- 后端首次启动时会自动建表
- 项目默认以空库启动，不会再自动写入预置任务或样本记录
- 首次进入系统需要先注册账号，再进行登录

## AI 接口说明

当前 AI 分析走统一服务层：

- `backend/app/services/ai_service.py`

真实模型适配代码位于：

- `backend/app/integrations/light_inspector/`

模型大文件资源默认位于：

- `backend/model_assets/light_inspector/`

其中 `best2.pt`、`score_total.tif`、`cover_huan1.tif` 为本地部署资源，默认不提交到 GitHub。

## 本地运行产物说明

以下目录或文件只应在本地存在，不应提交到 Git：

- `frontend/node_modules/`
- `backend/.venv/`
- `backend/.venv_bootstrap/`
- `backend/uploads/`
- `backend/light_inspector.db`

这些内容已经在 `.gitignore` 中排除。它们不进入 Git 不会影响别人运行，因为：

- 前端依赖可通过 `npm install` 重新安装
- 后端依赖可通过 `pip install -r requirements.txt` 重新安装
- 本地数据库和上传目录会在运行时自动生成

如果这些目录之前已经被提交到 Git，需要再执行一次：

```bash
git rm -r --cached backend/.venv backend/.venv_bootstrap frontend/node_modules backend/uploads
git rm --cached backend/light_inspector.db
git add .gitignore
git commit -m "chore: remove local runtime artifacts"
```
