from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# ---- simple in-memory storage ----
locations: Dict[str, dict] = {}

# ---- shared secret (simple security) ----
SHARED_TOKEN = "BearLovesMonkey"


class LocationUpdate(BaseModel):
    id: str
    token: str
    lat: float
    lon: float


@app.post("/update")
def update_location(data: LocationUpdate):
    if data.token != SHARED_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    locations[data.id] = {
        "lat": data.lat,
        "lon": data.lon,
    }

    return {"status": "ok"}


@app.get("/get/{user_id}")
def get_location(user_id: str):
    if user_id not in locations:
        raise HTTPException(status_code=404, detail="No location")

    return locations[user_id]
    