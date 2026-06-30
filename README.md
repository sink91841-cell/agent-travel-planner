# Agent Travel Planner

An intelligent multi-agent travel planning system powered by [HelloAgents](https://github.com/jjyaoao/HelloAgents) framework, integrating AMap (高德地图) MCP services for real-time POI search, weather queries, hotel recommendations, and route planning.

## Features

- **Multi-Agent Collaboration** — Four specialized agents (Attraction Search, Weather Query, Hotel Recommendation, Trip Planning) work together to generate comprehensive travel itineraries
- **AMap MCP Integration** — Real-time access to AMap geospatial services via MCP protocol: POI search, weather forecasts, and multi-modal route planning
- **Complete Trip Planning** — Generates daily itineraries including attractions with visit durations, meals (breakfast/lunch/dinner), hotel recommendations with pricing, and transportation suggestions
- **Budget Estimation** — Automatic cost breakdown for attractions, hotels, meals, and transportation
- **History Management** — Full CRUD operations on past trip plans with SQLite persistence
- **PDF Export** — One-click export trip plans to PDF (via html2canvas + jsPDF)
- **Modern Frontend** — Vue 3 + TypeScript + Ant Design Vue with responsive design

## Architecture

```
┌─────────────────────────┐     ┌──────────────────────────────────┐
│   Frontend (Vue 3)      │────▶│   Backend (FastAPI)              │
│   Port 5173             │     │   Port 8000                      │
│                         │     │                                  │
│   • Ant Design Vue UI   │     │   Multi-Agent System             │
│   • AMap JS API         │     │   ┌──────────────────────────┐   │
│   • PDF Export          │     │   │ Attraction Agent  (MCP)  │   │
│   • History CRUD        │     │   │ Weather Agent     (MCP)  │   │
└─────────────────────────┘     │   │ Hotel Agent      (MCP)  │   │
                                │   │ Planner Agent            │   │
                                │   └──────────────────────────┘   │
                                │              │                   │
                                │              ▼                   │
                                │   ┌──────────────────────────┐   │
                                │   │  AMap MCP Server          │   │
                                │   │  (amap-mcp-server)        │   │
                                │   └──────────────────────────┘   │
                                └──────────────────────────────────┘
```

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Agent Framework | HelloAgents (SimpleAgent + MCPTool) |
| API Framework | FastAPI + Pydantic v2 |
| MCP Server | amap-mcp-server (AMap MCP) |
| LLM Support | OpenAI, DeepSeek, and more |
| Database | SQLite (trip history) |
| HTTP Client | httpx, aiohttp |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | Vue 3.5 + Composition API |
| Language | TypeScript 5.7 |
| Build Tool | Vite 6 |
| UI Library | Ant Design Vue 4 |
| Map | AMap JavaScript API (Loader) |
| PDF Export | html2canvas + jsPDF |
| HTTP Client | Axios |

## Project Structure

```
agent-travel-planner/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── trip_planner_agent.py    # Multi-agent orchestration
│   │   ├── api/
│   │   │   ├── main.py                   # FastAPI app entry
│   │   │   └── routes/
│   │   │       ├── trip.py               # Trip planning endpoint
│   │   │       ├── history.py            # History CRUD endpoints
│   │   │       ├── map.py                # Map service endpoints
│   │   │       └── poi.py                # POI search endpoint
│   │   ├── services/
│   │   │   ├── llm_service.py            # LLM provider abstraction
│   │   │   ├── amap_service.py           # AMap API wrapper
│   │   │   └── trip_history_service.py   # SQLite history service
│   │   ├── models/
│   │   │   └── schemas.py                # Pydantic data models
│   │   └── config.py                     # Settings management
│   ├── requirements.txt
│   └── run.py                            # Uvicorn launcher
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue                  # Trip planner form
│   │   │   ├── Result.vue                # Trip plan display + PDF
│   │   │   └── History.vue               # History management
│   │   ├── services/
│   │   │   └── api.ts                    # Axios API client
│   │   ├── types/
│   │   │   └── index.ts                  # TypeScript interfaces
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── docs/                                  # Project documentation
├── start-all.ps1                          # Start both services
├── start-backend.ps1                      # Backend launcher
└── start-frontend.ps1                     # Frontend launcher
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- [AMap API Key](https://lbs.amap.com/) (Web Service API)
- LLM API Key (OpenAI / DeepSeek / compatible provider)

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
#   AMAP_API_KEY=your_amap_web_service_key
#   LLM_API_KEY=your_llm_api_key
#   LLM_BASE_URL=https://api.openai.com/v1  (optional)
#   LLM_MODEL_NAME=gpt-4o                     (optional)

# Start backend
python run.py
# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
# VITE_AMAP_JS_KEY=your_amap_js_api_key
# VITE_API_BASE_URL=http://localhost:8000

# Start dev server
npm run dev
# Frontend runs at http://localhost:5173
```

### Quick Start (Windows PowerShell)

```powershell
.\start-all.ps1
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/trip/plan` | Generate a trip plan |
| GET | `/api/trip/health` | Service health check |
| GET | `/api/history` | List all trip history |
| GET | `/api/history/{id}` | Get trip history detail |
| PUT | `/api/history/{id}` | Update a trip plan |
| DELETE | `/api/history/{id}` | Delete a trip plan |
| GET | `/api/map/poi` | Search POIs |
| GET | `/api/map/weather` | Query weather |
| POST | `/api/map/route` | Plan route |

Full interactive API documentation is available at `http://localhost:8000/docs` (Swagger UI).

## How It Works

1. User fills in trip preferences (city, dates, interests, budget, transportation) on the frontend form
2. Backend receives the request and kicks off the multi-agent pipeline:
   - **Attraction Agent** calls AMap MCP `maps_text_search` to discover POIs matching user preferences
   - **Weather Agent** calls AMap MCP `maps_weather` for forecasts during the trip dates
   - **Hotel Agent** calls AMap MCP `maps_text_search` to find accommodations near attractions
   - **Planner Agent** synthesizes all results into a structured JSON itinerary with daily plans
3. The itinerary is saved to SQLite history and returned to the frontend
4. User can view the trip on an interactive AMap, edit details, export to PDF, or revisit past plans

## AMap MCP Tools

The agents automatically invoke these AMap MCP tools:

- `maps_text_search` — POI search (attractions, hotels, restaurants)
- `maps_weather` — Weather forecast by city
- `maps_direction_walking_by_address` — Walking route between two addresses
- `maps_direction_driving_by_address` — Driving route between two addresses
- `maps_direction_transit_integrated_by_address` — Public transit route between two addresses

## License

CC BY-NC-SA 4.0

## Acknowledgements

- [HelloAgents](https://github.com/jjyaoao/HelloAgents) — Agent framework
- [amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) — AMap MCP server
- [AMap Open Platform](https://lbs.amap.com/) — Map & geospatial services
