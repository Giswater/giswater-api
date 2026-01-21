# 🚀 Giswater FastAPI Service

A lightweight, modular FastAPI application with **Swagger UI**, **Docker support**, **Keycloak authentication**, and **Gunicorn + Uvicorn** for production.

## 📂 Project Structure

```
giswater-api/
│── app/
│   │── .env.example         # Environment variable template
│   │
│   │── models/              # Pydantic models (organized by module)
│   │   │── basic/           # Basic module models
│   │   │── crm/             # CRM module models
│   │   │── epa/             # EPA hydraulic engine models
│   │   │── om/              # OM (mincut, waterbalance) models
│   │   │── routing/         # Routing module models
│   │   └── util_models.py   # Shared utility models
│   │
│   │── routers/             # API endpoints (organized by module)
│   │   │── basic/           # GIS feature queries
│   │   │── crm/             # Hydrometer CRUD
│   │   │── epa/             # SWMM & EPANET integration
│   │   │── om/              # Mincut operations
│   │   │── routing/         # Optimal path routing
│   │   └── waterbalance/    # DMA water balance
│   │
│   │── utils/               # Utilities and helpers
│   │   │── utils.py         # General utilities
│   │   └── routing_utils.py # Valhalla routing helpers
│   │
│   │── config.py            # Configuration loader
│   │── database.py          # Database connection manager
│   │── dependencies.py      # FastAPI dependencies
│   │── keycloak.py          # Keycloak OAuth2/OIDC integration
│   │── main.py              # FastAPI app entry point
│   └── static/              # Static files (favicon, etc.)
│
│── plugins/             # Plugin directory (see plugins/readme.md)
│── tests/               # Unit and integration tests
│── .github/workflows/   # CI/CD (flake8 lint, pytest)
│── Dockerfile           # Docker build config
│── gunicorn.conf.py     # Gunicorn production config
│── requirements.txt     # Python dependencies
└── README.md
```

## 🚀 Quick Start

### 1️⃣ **Clone the Repository**

```bash
git clone https://github.com/Giswater/giswater-api.git
cd giswater-api
```

### 2️⃣ **Set Up Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate  # for Windows PowerShell: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ **Run Locally**

```bash
uvicorn app.main:app --reload
```

📌 API Docs available at: [**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

---

## ⚙️ Configuration

Copy the env template and customize:

```bash
cp .env.example .env
```

### Environment Variables

**API toggles** (enable/disable modules):
```
API_BASIC=true
API_PROFILE=true
API_MINCUT=true
API_WATER_BALANCE=true
API_ROUTING=true
API_CRM=true
```

**Database**:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=giswater_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=ws
# DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

**Hydraulic engine** (EPA integration):
```
HYDRAULIC_ENGINE_ENABLED=true
HYDRAULIC_ENGINE_WS=true
HYDRAULIC_ENGINE_UD=true
HYDRAULIC_ENGINE_URL=localhost
```

**Keycloak** (optional):
```
KEYCLOAK_ENABLED=false
KEYCLOAK_URL=https://keycloak.example.com
KEYCLOAK_REALM=your-realm
KEYCLOAK_CLIENT_ID=giswater-api
KEYCLOAK_CLIENT_SECRET=your-secret
KEYCLOAK_ADMIN_CLIENT_SECRET=your-admin-secret
KEYCLOAK_CALLBACK_URI=http://localhost:8000/callback
```

---

## 🔐 Authentication

Keycloak integration is **optional**. When enabled:
- All endpoints require a valid JWT token
- Swagger UI shows "Authorize" button for OAuth2 flow
- User info available in routes via `get_current_user()` dependency

When disabled, endpoints are public and return an anonymous user context.

---

## 🔌 Plugins

Custom plugins can extend the API. Place plugin folders in `plugins/`:

```
plugins/
└── my-plugin/
    └── ...
```

Plugins are auto-loaded at startup. See [example plugin](https://github.com/Giswater/giswater-api-example-plugin).

---

## 🐳 Running with Docker

### **Build the Image**

```bash
docker build -t giswater-api .
```

### **Run the Container**

```bash
docker run -d -p 8000:8000 giswater-api
```

### **With Env File**

```bash
docker run -d -p 8000:8000 \
  --env-file .env \
  -v /var/log/giswater-api:/app/logs \
  giswater-api
```

### **Environment Variables**

Set the variables listed in the Configuration section (or via `--env-file`).

---

## 🏗️ Deployment (Gunicorn + Uvicorn)

For production, run:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
```

---

## 🛠️ API Endpoints

### Root & Health

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/`                               | GET    | Root endpoint (version info)                                                |
| `/health`                         | GET    | Health check (DB connection status)                                         |

### Basic Module

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/basic/getfeaturechanges`        | GET    | Fetch GIS features modified since specified date                            |
| `/basic/getinfofromcoordinates`   | GET    | Fetch GIS features info from coordinates                                    |
| `/basic/getselectors`             | GET    | Fetch current selectors                                                     |
| `/basic/getsearch`                | GET    | Search features                                                             |

### CRM Module

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/crm/hydrometers`                | POST   | Insert hydrometers (single or bulk)                                         |
| `/crm/hydrometers/{code}`         | PATCH  | Update single hydrometer by code                                            |
| `/crm/hydrometers`                | PATCH  | Update multiple hydrometers in bulk                                         |
| `/crm/hydrometers/{code}`         | DELETE | Delete single hydrometer by code                                            |
| `/crm/hydrometers`                | DELETE | Delete multiple hydrometers in bulk                                         |
| `/crm/hydrometers`                | PUT    | Replace all hydrometers (full sync mode)                                    |

### OM - Mincut

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/om/newmincut`                   | POST   | Create new mincut when anomaly detected in field                            |
| `/om/updatemincut`                | PATCH  | Update an existing mincut                                                   |
| `/om/valveunaccess`               | PUT    | Recalculate mincut due to inaccessible or inoperative valve                 |
| `/om/startmincut`                 | PUT    | Start mincut and interrupt water supply in affected zone                    |
| `/om/endmincut`                   | PUT    | End mincut and restore water supply in affected zone                        |
| `/om/repairmincut`                | PUT    | Perform repair without interrupting water supply (silent mincut)            |
| `/om/cancelmincut`                | PUT    | Cancel mincut and keep issue recorded for future resolution                 |
| `/om/deletemincut`                | DELETE | Delete mincut from system                                                   |

### OM - Water Balance

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/waterbalance/listdmas`          | GET    | Returns collection of DMAs                                                  |
| `/waterbalance/getdmahydrometers` | GET    | Retrieve DMA hydrometers data with location, status, and measurements       |
| `/waterbalance/getdmaparameters`  | GET    | Retrieves DMA parameters for performance analysis                           |

### EPA - Hydraulic Engine (UD)

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/epa/ud/getswmmfile`             | GET    | Get SWMM file data                                                          |
| `/epa/ud/setswmmfile`             | POST   | Modify SWMM file attributes                                                 |
| `/epa/ud/setnodevalue`            | PUT    | Modify node value in SWMM model                                             |
| `/epa/ud/setlinkvalue`            | PUT    | Modify link value in SWMM model                                             |
| `/epa/ud/setpumpvalue`            | PUT    | Modify pump value in SWMM model                                             |
| `/epa/ud/setoverflowvalue`        | PUT    | Modify overflow value in SWMM model                                         |
| `/epa/ud/setswmmresult`           | POST   | Set SWMM simulation result data                                             |
| `/epa/ud/setsolvetime`            | POST   | Set solve time for SWMM simulation                                          |
| `/epa/ud/setcontrolvalue`         | PUT    | Modify control value in SWMM model                                          |

### EPA - Hydraulic Engine (WS)

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/epa/ws/getepafile`              | GET    | Get EPA file data                                                           |
| `/epa/ws/setepafile`              | POST   | Modify EPA file attributes                                                  |
| `/epa/ws/sethydrantreachability`  | PUT    | Set hydrant reachability in EPANET model                                    |
| `/epa/ws/setreservoirvalue`       | PUT    | Update reservoir value in EPANET model                                      |
| `/epa/ws/setlinkvalue`            | PUT    | Update link value in EPANET model                                           |
| `/epa/ws/setvalvevalue`           | PUT    | Modify valve value in EPANET model                                          |
| `/epa/ws/settankvalue`            | PUT    | Modify tank value in EPANET model                                           |
| `/epa/ws/setpumpvalue`            | PUT    | Modify pump value in EPANET model                                           |
| `/epa/ws/setjunctionvalue`        | PUT    | Modify junction value in EPANET model                                       |
| `/epa/ws/setpatternvalue`         | PUT    | Modify pattern value in EPANET model                                        |
| `/epa/ws/setcontrolsvalue`        | PUT    | Modify controls value in EPANET model                                       |
| `/epa/ws/setsolveh`               | POST   | Run pressure & flow simulation in EPANET                                    |
| `/epa/ws/setsolveq`               | POST   | Run water quality simulation in EPANET                                      |

### OM - Routing

| Endpoint                             | Method | Description                                                              |
| ------------------------------------ | ------ | ------------------------------------------------------------------------ |
| `/routing/getobjectoptimalpathorder` | GET    | Get optimal path through network points using Valhalla routing engine    |
| `/routing/getobjectparameterorder`   | GET    | Get features ordered by parameter                                        |

---

## ✅ Testing & Linting

### Run Tests

```bash
pytest
```

### Run Linter

```bash
flake8
```

CI/CD runs both on push via GitHub Actions (`.github/workflows/`).

---

## 📌 License

This project is free software, licensed under the GNU General Public License (GPL) version 3 or later. Refer to the [LICENSE](./LICENSE) file for details.

