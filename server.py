from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os

app = FastAPI()

# Allow HTML file to call API from browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# User tokens (hardcoded for now)
USERS = {
    "him-token-abc123": "him",
    "her-token-xyz789": "her"
}

DB_FILE = "events.json"

# Event model
class Event(BaseModel):
    id: int
    title: str
    date: str
    time: Optional[str] = ""
    endTime: Optional[str] = ""
    place: Optional[str] = ""
    notes: Optional[str] = ""
    who: str
    author: str

# Load/save helpers
def load_events():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return []

def save_events(events):
    with open(DB_FILE, 'w') as f:
        json.dump(events, f, indent=2)

# Auth helper
def get_user(token: str):
    if token not in USERS:
        raise HTTPException(status_code=401, detail="Invalid token")
    return USERS[token]

# API Endpoints
@app.get("/events")
def get_events(x_user_token: str = Header(...)):
    user = get_user(x_user_token)
    return load_events()

@app.post("/events")
def create_event(event: Event, x_user_token: str = Header(...)):
    user = get_user(x_user_token)
    event.author = user
    events = load_events()
    events.append(event.dict())
    save_events(events)
    return event

@app.put("/events/{event_id}")
def update_event(event_id: int, event: Event, x_user_token: str = Header(...)):
    user = get_user(x_user_token)
    events = load_events()
    for i, e in enumerate(events):
        if e['id'] == event_id:
            events[i] = event.dict()
            save_events(events)
            return event
    raise HTTPException(status_code=404, detail="Event not found")

@app.delete("/events/{event_id}")
def delete_event(event_id: int, x_user_token: str = Header(...)):
    user = get_user(x_user_token)
    events = load_events()
    events = [e for e in events if e['id'] != event_id]
    save_events(events)
    return {"deleted": event_id}
