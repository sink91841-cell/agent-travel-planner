# Agent Travel Planner（智能旅行助手）

基于 [HelloAgents](https://github.com/jjyaoao/HelloAgents) 多智能体框架打造的智能旅行规划系统。系统通过**四个专业 Agent 协作**，自动调用高德地图 MCP 服务获取真实的景点、天气、酒店和路线数据，生成包含每日行程、餐饮推荐、住宿安排和预算明细的完整旅行计划。

---

## 功能特点

### 核心能力

- **多智能体协作规划** — 四个专业 Agent（景点搜索、天气查询、酒店推荐、行程规划）分工协作，各自调用相应的工具获取真实数据，最后由规划 Agent 整合生成完整行程
- **高德地图 MCP 集成** — 通过 MCP 协议接入高德地图服务，提供实时 POI 搜索、天气预报、步行/驾车/公交路线规划能力
- **完整的旅行计划** — 每人每天 2-3 个景点（含游览时长和门票价格）、早中晚三餐推荐、酒店推荐（含价格区间和评分）、交通方式建议
- **预算自动估算** — 自动计算景点门票、酒店住宿、餐饮费用、交通费用的分项汇总和总预算
- **行程编辑与导出** — 支持在线编辑景点顺序和内容，一键导出为高清图片（PNG）或 PDF 文件
- **历史记录管理** — 通过 SQLite 持久化所有旅行计划，支持查看、编辑、删除历史记录
- **响应式前端界面** — Vue 3 + Ant Design Vue 打造的现代化界面，渐变色设计、动画过渡，适配桌面和移动端

### 前端页面

| 页面 | 路由 | 功能说明 |
|------|------|----------|
| 首页（规划表单） | `/` | 三步式表单：目的地与日期 → 偏好设置 → 额外要求，带实时天数和进度动画 |
| 结果页 | `/result/:historyId` | 侧边导航 + 可折叠每日行程 + 概览/预算/天气卡片 + 编辑模式 + 图片/PDF 导出 |
| 历史记录 | `/history` | 表格展示所有历史计划，支持查看详情和一键删除 |

### 行程计划包含的内容

每个旅行计划会包含以下完整信息：

- **行程概览**：城市、起止日期、总体建议
- **每日行程**（可折叠面板）：
  - 行程描述、交通方式、住宿类型
  - 景点安排（名称、地址、游览时长、描述、门票价格）
  - 酒店推荐（名称、地址、类型、价格区间、评分、距景点距离）
  - 餐饮安排（早餐、午餐、晚餐的推荐和描述）
- **天气信息**：每天的白天/夜间天气、温度、风向风力
- **预算明细**：景点门票、酒店住宿、餐饮、交通四项的分类汇总和总计

---

## 系统架构

```
┌──────────────────────────────┐     ┌─────────────────────────────────────────┐
│   前端 (Vue 3 + TypeScript)   │────▶│   后端 (FastAPI)                         │
│   端口 5173                   │     │   端口 8000                              │
│                              │     │                                          │
│   • 规划表单 (Home.vue)       │     │   POST /api/trip/plan                    │
│   • 结果展示 (Result.vue)     │     │         ↓                                │
│   • 历史管理 (History.vue)    │     │   ┌──────────────────────────────────┐   │
│   • 图片/PDF 导出             │     │   │     多智能体协作流程              │   │
│   • 在线编辑行程              │     │   │                                  │   │
└──────────────────────────────┘     │   │  步骤1: 景点搜索Agent              │   │
                                     │   │    ↓ 调用 maps_text_search (MCP)  │   │
                                     │   │                                  │   │
                                     │   │  步骤2: 天气查询Agent              │   │
                                     │   │    ↓ 调用 maps_weather (MCP)      │   │
                                     │   │                                  │   │
                                     │   │  步骤3: 酒店推荐Agent              │   │
                                     │   │    ↓ 调用 maps_text_search (MCP)  │   │
                                     │   │                                  │   │
                                     │   │  步骤4: 行程规划Agent              │   │
                                     │   │    ↓ 整合所有数据 → JSON 行程      │   │
                                     │   └──────────────────────────────────┘   │
                                     │              │                            │
                                     │              ▼                            │
                                     │   ┌──────────────────────────────────┐   │
                                     │   │  SQLite 历史记录                  │   │
                                     │   │  (data/trip_history.db)           │   │
                                     │   └──────────────────────────────────┘   │
                                     └─────────────────────────────────────────┘
```

---

## 技术栈

### 后端

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| Agent 框架 | HelloAgents (SimpleAgent + MCPTool) | 四个 Agent 各自独立的 system prompt |
| Web 框架 | FastAPI + Pydantic v2 | 异步 API，自动生成 Swagger 文档 |
| MCP 服务 | amap-mcp-server | 高德地图 MCP 协议服务端 |
| LLM 支持 | OpenAI / DeepSeek 等兼容接口 | 通过 HelloAgentsLLM 统一调用 |
| 数据库 | SQLite | 旅行计划历史记录持久化 |
| HTTP 客户端 | httpx + aiohttp | 异步 HTTP 请求 |
| 日志 | loguru | 结构化日志输出 |

### 前端

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 框架 | Vue 3.5 + Composition API | `<script setup>` 语法 |
| 语言 | TypeScript 5.7 | 完整类型定义 |
| 构建工具 | Vite 6 | 极速 HMR 开发体验 |
| UI 库 | Ant Design Vue 4 | 卡片、表格、折叠面板、日期选择器等 |
| 地图展示 | 高德地图 JavaScript API | 景点标记和信息窗体 |
| PDF 导出 | jsPDF + html2canvas | Canvas 渲染 → PDF 分页输出 |
| HTTP 客户端 | Axios | 拦截器统一处理请求/响应 |

---

## 项目结构

```
agent-travel-planner/
├── backend/                                  # 后端服务
│   ├── app/
│   │   ├── agents/
│   │   │   └── trip_planner_agent.py         # 多智能体编排核心（500+ 行）
│   │   │                                      #   - 4 个 Agent 的定义和提示词
│   │   │                                      #   - MCP 工具创建和绑定
│   │   │                                      #   - 多步骤协作流程
│   │   │                                      #   - JSON 解析和备用方案
│   │   ├── api/
│   │   │   ├── main.py                        # FastAPI 应用入口 + CORS + 路由注册
│   │   │   └── routes/
│   │   │       ├── trip.py                    # POST /api/trip/plan — 旅行规划
│   │   │       ├── history.py                 # GET/PUT/DELETE /api/history — 历史 CRUD
│   │   │       ├── map.py                     # GET /api/map/* — 地图服务接口
│   │   │       └── poi.py                     # GET /api/poi/* — POI 搜索接口
│   │   ├── services/
│   │   │   ├── llm_service.py                 # LLM 提供商抽象层
│   │   │   ├── amap_service.py                # 高德地图 API 包装
│   │   │   └── trip_history_service.py        # SQLite 历史服务（增删改查）
│   │   ├── models/
│   │   │   └── schemas.py                     # Pydantic 数据模型（10+ 个模型类）
│   │   └── config.py                          # Pydantic Settings 配置管理
│   ├── data/                                   # SQLite 数据库文件（gitignore）
│   ├── tests/                                  # 后端测试
│   ├── requirements.txt                        # Python 依赖清单
│   ├── run.py                                  # Uvicorn 启动脚本
│   └── .env.example                            # 环境变量模板
├── frontend/                                   # 前端应用
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue                        # 首页：三步表单 + 进度动画（650+ 行）
│   │   │   ├── Result.vue                      # 结果页：行程展示 + 编辑 + 导出（1140+ 行）
│   │   │   └── History.vue                     # 历史页：表格管理（270+ 行）
│   │   ├── services/
│   │   │   └── api.ts                          # Axios 客户端 + 全部 API 函数
│   │   ├── types/
│   │   │   └── index.ts                        # TypeScript 接口定义（20+ 个类型）
│   │   ├── App.vue                             # 根组件（路由视图 + 导航栏）
│   │   └── main.ts                             # 应用入口
│   ├── package.json
│   └── vite.config.ts
├── docs/                                        # 项目文档
├── start-all.ps1                                # 一键启动前后端
├── start-backend.ps1                            # 后端启动脚本
├── start-frontend.ps1                           # 前端启动脚本
├── .gitignore                                   # Git 忽略规则
└── README.md
```

---

## 快速开始

### 环境要求

- **Python** 3.10 及以上
- **Node.js** 16 及以上
- **高德地图 API Key**（需要 Web 服务 API 和 Web 端 JS API）
- **LLM API Key**（支持 OpenAI、DeepSeek 等兼容接口）

### 后端安装

```bash
# 1. 进入后端目录
cd backend

# 2. 创建并激活虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key：
#   AMAP_API_KEY=你的高德Web服务API密钥
#   LLM_API_KEY=你的LLM_API密钥
#   LLM_BASE_URL=https://api.openai.com/v1  （可选，默认 OpenAI）
#   LLM_MODEL_NAME=gpt-4o                     （可选）

# 5. 启动后端
python run.py
# 后端运行在 http://localhost:8000
# API 文档在 http://localhost:8000/docs
```

### 前端安装

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 创建环境变量文件 .env，内容如下：
#   VITE_AMAP_JS_KEY=你的高德JS API密钥
#   VITE_API_BASE_URL=http://localhost:8000

# 4. 启动开发服务器
npm run dev
# 前端运行在 http://localhost:5173
```

### 一键启动（Windows PowerShell）

```powershell
.\start-all.ps1
```

---

## 多智能体协作流程

整个旅行计划的生成由四个专业 Agent 顺序协作完成，每个 Agent 都有独立的 system prompt（系统提示词）和工具权限：

### 步骤 1：景点搜索 Agent（Attraction Agent）

- **职责**：根据用户的目的地城市和旅行偏好（历史文化/自然风光/艺术/休闲）搜索合适的景点
- **工具**：`maps_text_search`（高德地图 MCP）
- **输入**：`keywords=偏好关键词,city=城市名`
- **输出**：该城市的景点 POI 列表（含名称、地址、经纬度、类别）
- **约束**：只返回旅游景点、博物馆、公园、古迹、自然景区，排除餐馆、酒店、商场

### 步骤 2：天气查询 Agent（Weather Agent）

- **职责**：查询目的地城市在旅行日期范围内的天气情况
- **工具**：`maps_weather`（高德地图 MCP）
- **输入**：`city=城市名`
- **输出**：每日天气信息（白天/夜间天气、温度、风向风力）

### 步骤 3：酒店推荐 Agent（Hotel Agent）

- **职责**：根据用户的住宿偏好（经济型/舒适型/豪华/民宿）搜索合适的酒店
- **工具**：`maps_text_search`（高德地图 MCP）
- **输入**：`keywords=酒店,city=城市名`
- **输出**：酒店列表（含名称、地址、价格、评分、位置）

### 步骤 4：行程规划 Agent（Planner Agent）

- **职责**：整合前三步的所有信息，生成结构化的完整旅行计划
- **工具**：无（纯 LLM 推理）
- **输入**：景点数据 + 天气数据 + 酒店数据 + 用户偏好
- **输出**：严格的 JSON 格式行程计划（含每日行程、餐饮、酒店、天气、预算）
- **约束**：每天 2-3 个景点、必须含早中晚三餐、经纬度坐标必须真实、预算分类汇总

### 容错机制

如果任何步骤失败或 LLM 返回的数据无法解析，系统会使用 `_create_fallback_plan()` 方法生成一个基于基础模板的备用计划，确保用户始终能获得可用结果。

---

## API 接口文档

启动后端后，访问 `http://localhost:8000/docs` 可查看完整的 Swagger 交互式 API 文档。

### 旅行规划

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/trip/plan` | 生成旅行计划 |
| GET | `/api/trip/health` | 服务健康检查（含 Agent 和工具数量） |

**POST /api/trip/plan 请求体示例：**

```json
{
  "city": "北京",
  "start_date": "2026-07-01",
  "end_date": "2026-07-03",
  "travel_days": 3,
  "transportation": "公共交通",
  "accommodation": "舒适型酒店",
  "preferences": ["历史文化", "美食"],
  "free_text_input": "想去故宫和长城，对海鲜过敏"
}
```

**响应示例：**

```json
{
  "success": true,
  "message": "旅行计划生成成功",
  "history_id": "a1b2c3d4-...",
  "data": {
    "city": "北京",
    "start_date": "2026-07-01",
    "end_date": "2026-07-03",
    "days": [
      {
        "date": "2026-07-01",
        "day_index": 0,
        "description": "抵达北京，游览天安门广场和故宫...",
        "transportation": "公共交通",
        "accommodation": "舒适型酒店",
        "hotel": {
          "name": "北京某某酒店",
          "address": "东城区...",
          "location": { "longitude": 116.397, "latitude": 39.916 },
          "price_range": "400-600元",
          "rating": "4.5",
          "distance": "距故宫1.5公里",
          "type": "舒适型酒店",
          "estimated_cost": 500
        },
        "attractions": [
          {
            "name": "故宫博物院",
            "address": "北京市东城区景山前街4号",
            "location": { "longitude": 116.397, "latitude": 39.916 },
            "visit_duration": 180,
            "description": "明清两代的皇家宫殿...",
            "category": "历史文化",
            "ticket_price": 60
          }
        ],
        "meals": [
          { "type": "breakfast", "name": "酒店自助早餐", "description": "...", "estimated_cost": 30 },
          { "type": "lunch", "name": "故宫附近餐厅", "description": "...", "estimated_cost": 50 },
          { "type": "dinner", "name": "王府井美食街", "description": "...", "estimated_cost": 80 }
        ]
      }
    ],
    "weather_info": [
      {
        "date": "2026-07-01",
        "day_weather": "晴",
        "night_weather": "多云",
        "day_temp": 32,
        "night_temp": 22,
        "wind_direction": "南风",
        "wind_power": "1-3级"
      }
    ],
    "overall_suggestions": "建议提前预约故宫门票...",
    "budget": {
      "total_attractions": 180,
      "total_hotels": 1500,
      "total_meals": 480,
      "total_transportation": 200,
      "total": 2360
    }
  }
}
```

### 历史记录管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/history` | 获取所有历史记录列表（按时间倒序） |
| GET | `/api/history/{id}` | 获取单条历史记录详情（含完整行程 JSON） |
| PUT | `/api/history/{id}` | 更新历史记录中的旅行计划 |
| DELETE | `/api/history/{id}` | 删除历史记录（返回 204） |

### 地图服务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/map/poi` | 搜索 POI 兴趣点 |
| GET | `/api/map/weather` | 查询天气信息 |
| POST | `/api/map/route` | 规划出行路线 |

---

## 高德地图 MCP 工具列表

系统 Agent 可以自动调用以下高德地图 MCP 工具：

| 工具名称 | 功能 | 典型用途 |
|---------|------|---------|
| `maps_text_search` | 关键词搜索 POI | 搜景点、酒店、餐厅 |
| `maps_weather` | 城市天气查询 | 获取旅行期间的天气预报 |
| `maps_direction_walking_by_address` | 步行路线规划 | 相邻景点间步行导航 |
| `maps_direction_driving_by_address` | 驾车路线规划 | 自驾游路线规划 |
| `maps_direction_transit_integrated_by_address` | 公交路线规划 | 公共交通换乘方案 |

---

## 配置说明

### 后端环境变量（backend/.env）

```env
# 应用配置
APP_NAME=Agent Travel Planner
DEBUG=false
HOST=0.0.0.0
PORT=8000

# LLM 配置（OpenAI 兼容接口）
LLM_API_KEY=sk-your-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o

# 高德地图配置
AMAP_API_KEY=你的高德Web服务API密钥

# 数据目录
DATA_DIR=./data
```

### 前端环境变量（frontend/.env）

```env
# 高德地图 JS API Key（用于前端地图展示）
VITE_AMAP_JS_KEY=你的高德JS API密钥

# 后端 API 地址
VITE_API_BASE_URL=http://localhost:8000
```

---

## 使用指南

### 生成旅行计划

1. 打开浏览器访问 `http://localhost:5173`
2. **第一步**：填写目的地城市、开始日期和结束日期（系统自动计算天数）
3. **第二步**：选择交通方式（公共交通/自驾/步行/混合）、住宿偏好（经济型/舒适型/豪华/民宿）、旅行风格标签（历史文化/自然风光/美食/购物/艺术/休闲）
4. **第三步**（可选）：在文本框中填写额外要求，例如"想看升旗"、"需要无障碍设施"、"对海鲜过敏"等
5. 点击 **"开始规划我的旅行"** 按钮
6. 等待约 30-60 秒（期间进度条会显示当前阶段：搜索景点 → 查询天气 → 推荐酒店 → 生成行程）
7. 自动跳转到结果页面

### 查看和编辑行程

- **侧边导航**：点击跳转到概览/预算/某一天/天气信息
- **每日行程**：可折叠面板展示，点击展开查看详情
- **编辑模式**：点击"编辑行程"可修改景点名称、地址、时长、描述、门票；支持拖拽调整顺序、删除景点
- **导出功能**：支持导出为高清 PNG 图片或 A4 格式 PDF 文件

### 管理历史记录

- 访问 `/history` 页面查看所有历史计划
- 表格显示城市、天数、日期、交通、住宿、创建时间
- 支持查看详情和删除

---

## 开源协议

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 协议。

- **BY（署名）**：使用或分享时必须标注原作者
- **NC（非商业性使用）**：不得用于商业目的
- **SA（相同方式共享）**：修改后必须以相同协议发布

---

## 致谢

- [HelloAgents 教程](https://github.com/datawhalechina/Hello-Agents) — 智能体学习资源
- [HelloAgents 框架](https://github.com/jjyaoao/HelloAgents) — 多智能体框架
- [高德地图开放平台](https://lbs.amap.com/) — 地图与位置服务
- [amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) — 高德地图 MCP 服务端
- [Ant Design Vue](https://antdv.com/) — Vue 3 UI 组件库
