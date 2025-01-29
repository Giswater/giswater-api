import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import features, mincut, water_balance, digital_twin

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(features.router)
app.include_router(mincut.router)
app.include_router(water_balance.router)
app.include_router(digital_twin.router)

@app.get("/")
async def root():
    return {"message": "FastAPI Application"}

# Favicon endpoint
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join("app", "static", "favicon.ico")
    return FileResponse(favicon_path)
