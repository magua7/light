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
│  ├─ scripts/
│  │  └─ bootstrap_backend.py
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

- `backend/uploads/`、`backend/light_inspector.db`、`frontend/node_modules/`、`backend/.venv/`、`backend/.venv_bootstrap/` 属于本地运行产物，不应提交到 Git。
- 仓库里保留的是源码、依赖清单和启动说明；拉取代码后可在本地重新安装依赖并自动生成运行数据。

## 已实现功能

- 登录 / 注册
- 首页大屏统计
- 上传检测任务
- 检测报告详情
- 历史记录查询
- 地图监测展示
- 预警列表与状态切换

## 环境要求

- Windows 10/11
- Python 3.10 或更高版本
- Node.js LTS
- 请确保 `python` 和 `npm` 已加入 PATH

如果你是从 GitHub 拉取项目，不要直接复用别人机器里的 `.venv` 或 `node_modules`。这些目录属于本地环境，应由脚本在你的电脑上重新创建。

## 推荐启动方式

### Windows 图形方式

可直接双击根目录下的脚本：

- `start_project.bat`：同时启动前后端
- `start_backend.bat`：只启动后端
- `start_frontend.bat`：只启动前端

其中：

- `start_backend.bat` 只负责检查系统里是否有 Python，并调用 `backend/scripts/bootstrap_backend.py`
- `bootstrap_backend.py` 会自动检查 Python 版本、准备虚拟环境、安装依赖并启动 FastAPI
- 如果 `.venv` 已损坏或来自别的机器，脚本会自动重建
- 如果 `.venv` 被占用删不掉，脚本会自动回退到 `.venv_bootstrap`
- pip 默认源失败后，会自动用清华镜像重试一次
- 如果检测到代理变量，还会额外给出更明确的网络/代理提示
- 前端脚本会自动检测 `node` 和 `npm`
- `node_modules` 不存在或不完整时，会自动执行 `npm ci` 或 `npm install`
- npm 默认源失败时，会自动重试 `npmmirror`

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

- 后端：`http://127.0.0.1:8000`
- 后端健康检查：`http://127.0.0.1:8000/api/health`
- 前端：`http://127.0.0.1:5173`

## 后端启动器会自动做什么

`backend/scripts/bootstrap_backend.py` 会按下面流程执行：

1. 检查当前系统 Python 版本是否至少为 3.10
2. 优先检查 `backend/.venv`
3. 如果 `.venv` 无效，尝试删除并重建
4. 如果 `.venv` 被占用删不掉，自动回退到 `backend/.venv_bootstrap`
5. 使用虚拟环境里的 Python 执行：
   - `python -m pip install --upgrade pip`
   - `python -m pip install -r requirements.txt`
6. 最后启动：
   - `python -m uvicorn app.main:app --reload`

整个过程都不会依赖作者电脑上的 Python 绝对路径。

## 常见问题

### 1. 出现 `No Python at "E:\python3.10\python.exe"`

这通常说明仓库里混入了作者电脑上生成的旧 `.venv`。Windows 虚拟环境会在内部记录创建它时使用的基础 Python 路径，换一台电脑后这个路径就失效了。

现在的启动方式不会再直接依赖旧 `.venv`，而是会自动检测并重建无效环境。

### 2. 出现 `Existing .venv is missing pyvenv.cfg`

这说明当前 `.venv` 已损坏、不完整，或者只是被拷贝了部分目录。

现在的 Python 启动器会：

- 先尝试删除旧 `.venv`
- 如果删除失败，再自动回退到 `.venv_bootstrap`
- 尽量继续完成初始化，而不是直接卡死

如果你自己本机仍然删不掉 `.venv`，通常是因为某个终端、编辑器或 Python 进程还在占用它。关闭占用进程后再运行即可。

### 3. 出现 `Could not find a version that satisfies the requirement fastapi==0.115.6`

大多数情况下，这并不意味着 `fastapi==0.115.6` 不存在，而是 pip 没能正常访问 PyPI。

常见原因：

- 网络连接失败
- `HTTP_PROXY` / `HTTPS_PROXY` 指向了不可用代理
- `PIP_INDEX_URL` 指向了不可访问的镜像

启动器现在会：

- 先用默认源安装
- 失败后自动重试清华镜像
- 输出更明确的提示，说明这通常是网络或代理问题

手动重试示例：

```bash
cd backend
.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

## 首次运行说明

- 后端启动后会自动建表
- 会自动生成一批演示用种子数据
- 默认演示点位位于湖南长沙范围
- 首页和地图页会直接显示这些样本
- 首次进入系统需要先注册账号，再登录

## 程序入口

- 后端入口：[backend/app/main.py](D:/计设/lightInspector/backend/app/main.py)
- 后端启动器：[backend/scripts/bootstrap_backend.py](D:/计设/lightInspector/backend/scripts/bootstrap_backend.py)
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
- `backend/.venv_bootstrap/`
- `backend/uploads/`
- `backend/light_inspector.db`

这些目录已经在 `.gitignore` 中排除。它们不进 Git 不会影响别人运行，因为：

- 前端依赖可通过 `npm install` 重新安装
- 后端依赖可通过 `pip install -r requirements.txt` 重新安装
- 数据库和上传目录会在本地运行时自动生成
- 启动脚本不会依赖任何作者本机的绝对路径

如果这些目录之前已经被提交到 Git，需要再执行一次从版本控制中移除：

```bash
git rm -r --cached backend/.venv backend/.venv_bootstrap frontend/node_modules backend/uploads
git rm --cached backend/light_inspector.db
git add .gitignore
git commit -m "chore: remove local runtime artifacts"
```
