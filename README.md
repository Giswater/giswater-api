# 🚀 Giswater FastAPI Service

A lightweight, modular FastAPI application with **Swagger UI**, **Docker support**, and **Gunicorn + Uvicorn** for production.

## 📂 Project Structure

```
giswater_api_server/
│── app/
│   │── config/         # Configuration files folder
|   |   |── app.config  # Main configuration file (an app.config_example is provided, change its name or create a copy)
│   │
│   │── models/         # Pydantic models to use as input parameters
│   │── routers/        # API endpoints (organized by type)
│   │── services/       # Business logic and processing
│   │── database.py     # Functions to connect to the database
│   │── main.py         # Entry point of the FastAPI app
│   │── utils.py        # Functions and utilities
│
│── tests/              # Unit and integration tests
│── .gitignore          # Git ignore rules
│── requirements.txt    # Python dependencies
│── Dockerfile          # Dockerization setup
│── gunicorn.conf.py    # Gunicorn configuration
│── README.md           # Project documentation
│── requirements.txt    # Requirement packages
```

## 🚀 Quick Start

### 1️⃣ **Clone the Repository**

```bash
git clone https://github.com/Giswater/giswater_api_server.git
cd giswater_api_server
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

## 🐳 Running with Docker

### **Build the Image**

```bash
docker build -t giswater_api_server .
```

### **Run the Container**

```bash
docker run -d -p 8000:8000 giswater_api_server
```

---

## 🏗️ Deployment (Gunicorn + Uvicorn)

For production, run:

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app
```

---

## 🛠️ API Endpoints

### Root & Basic

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/`                               | GET    | Root endpoint                                                               |
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

## ✅ Testing

Run tests using `pytest`:

```bash
pytest
```

---

## 📌 License

This project is free software, licensed under the GNU General Public License (GPL) version 3 or later. Refer to the [LICENSE](./LICENSE) file for details.

