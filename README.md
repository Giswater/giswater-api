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

| Endpoint                          | Method | Description                                                                 |
| --------------------------------- | ------ | --------------------------------------------------------------------------- |
| `/`                               | GET    | Root endpoint                                                               |
| `/features/getfeaturechanges`     | GET    | Fetch feature changes for GMAO                                              |
| `/mincut/newmincut`               | POST   | Create new mincut                                                           |
| `/mincut/updatemincut`            | PUT    | Update an existing mincut                                                   |
| `/mincut/valveunaccess`           | PUT    | Recalculate mincut due to an inaccessible or inoperative valve              |
| `/mincut/startmincut`             | PUT    | Start the mincut and interrupt water supply in the affected zone            |
| `/mincut/endmincut`               | PUT    | End the mincut and restore water supply in the affected zone                |
| `/mincut/repairmincut`            | PUT    | Perform repair without interrupting water supply (silent mincut)            |
| `/mincut/cancelmincut`            | PUT    | Cancel the mincut and keep the issue recorded for future resolution         |
| `/waterbalance/getdmahydrometers` | GET    | Retrieve DMA hydrometers data                                               |
| `/digitaltwin/getepafile`         | GET    | Get EPA file data                                                           |

---

## ✅ Testing

Run tests using `pytest`:

```bash
pytest
```

---

## 📌 License

This project is free software, licensed under the GNU General Public License (GPL) version 3 or later. Refer to the [LICENSE](./LICENSE) file for details.

