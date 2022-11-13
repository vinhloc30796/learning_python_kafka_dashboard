# Base
import json
import logging
from datetime import datetime
from typing import Dict, List

# Server
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Owned
from database import redis
from models import Event, Delivery
import consumers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)


def build_state(pk: str) -> Dict:
    pks = Event.all_pks()
    all_events = [Event.get(_pk) for _pk in pks]
    filtered_events = sorted(
        [event for event in all_events if event.delivery_id == pk], 
        key=lambda event: event.created_at
    )
    # filtered_events.sort(key=lambda event: event.created_at)
    logging.info(f"Found {len(filtered_events)} events for delivery {pk} (out of {len(all_events)})")
    state = {}
    for event in filtered_events:
        state = consumers.CONSUMERS[event.type](state, event)
    return state


@app.get("/deliveries/{pk}/status")
async def get_state(pk: str) -> Dict:
    state = redis.get(f"delivery:{pk}") # defaults to None
    if state:
        return json.loads(state)

    state = build_state(pk)
    return state


@app.post("/deliveries/create")
async def create_delivery(request: Request):
    body = await request.json()
    # Delivery
    delivery = Delivery(**body["data"])
    # Event
    event = Event(
        created_at=datetime.now().timestamp(),
        delivery_id=delivery.pk,
        type=body["type"],
        data=json.dumps(body["data"]),
    )
    # State
    state = consumers.CONSUMERS[event.type]({}, event)
    # Save
    delivery.save()
    event.save()
    redis.set(f"delivery:{delivery.pk}", json.dumps(state))
    return state


@app.post("/event")
async def dispatch(request: Request):
    # Historical
    body = await request.json()
    delivery_id = body["delivery_id"]
    event = Event(
        created_at=datetime.now().timestamp(),
        delivery_id=delivery_id,
        type=body["type"],
        data=json.dumps(body["data"]),
    )
    state = await get_state(delivery_id)
    # New state
    new_state = consumers.CONSUMERS[event.type](state, event)
    # Save
    event.save()
    redis.set(f"delivery:{delivery_id}", json.dumps(new_state))
    return new_state
