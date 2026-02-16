from fastapi import FastAPI, HTTPException, Header
from typing import Optional
import os

app = FastAPI(title="Love Compass API")

# =========================================================
# SECURITY CONFIG
# =========================================================

# Secret token (set in environment when hosting)
API_TOKEN = os.environ.get("API_TOKEN", "DEV_SECRET_CHANGE_ME")

# Only these device IDs are allowed
ALLOWED_DEVICES = {"bear", "monkey"}

# =========================================================
# STORAGE (in memory)
# =========================================================

# Example:
# {
#   "bear": (lat, lon),
#   "monkey": (lat, lon)
# }
locations = {}

# =========================================================
# HELPERS
# =========================================================

def verify_token(authorization: Optional[str]):
    """Check Authorization header"""
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


def verify_device(device_id: str):
    """Check if device is allowed"""
    if device_id not in ALLOWED_DEVICES:
        raise HTTPException(status_code=403, detail="Unknown device")


# =========================================================
# ROUTES
# =========================================================

@app.get("/")
def root():
    return {"status": "Love Compass server running"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------
# UPDATE LOCATION
# ---------------------------------------------------------
@app.post("/update")
def update_location(
    data: dict,
    authorization: Optional[str] = Header(None)
):
    """
    Body:
    {
        "id": "bear",
        "lat": 48.123,
        "lon": 11.567
    }
    """

    verify_token(authorization)

    device_id = data.get("id")
    lat = data.get("lat")
    lon = data.get("lon")
    print(f"💌 Update request: device={device_id}")

    if device_id is None or lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Missing fields")

    verify_device(device_id)

    locations[device_id] = (lat, lon)

    print(f"Location update from {device_id}: {lat}, {lon}")

    return {"status": "ok"}


# ---------------------------------------------------------
# GET PARTNER LOCATION
# ---------------------------------------------------------
@app.get("/get/{device_id}")
def get_partner_location(
    device_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Device asks for the OTHER device location
    """

    verify_token(authorization)
    verify_device(device_id)

    # find partner
    partners = ALLOWED_DEVICES - {device_id}

    if not partners:
        raise HTTPException(status_code=404, detail="No partner configured")

    partner_id = list(partners)[0]

    if partner_id not in locations:
        raise HTTPException(status_code=404, detail="Partner location unknown")

    lat, lon = locations[partner_id]

    return {
        "id": partner_id,
        "lat": lat,
        "lon": lon
    }

# Stores connections
connections = {}  # e.g., {"BearLovesMonkey": ["bear", "monkey"]}

@app.post("/join")
def join_connection(data: dict, authorization: Optional[str] = Header(None)):
    verify_token(authorization)
    name = data.get("name")
    device_id = data.get("device_id")
    print(f"💌 Join request: device={device_id}")

    if not name or not device_id:
        raise HTTPException(status_code=400, detail="Missing fields")

    if name not in connections:
        connections[name] = []

    if device_id not in connections[name]:
        connections[name].append(device_id)

    return {"status": "joined", "devices": connections[name]}