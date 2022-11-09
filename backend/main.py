# Base
import json
import logging
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


@app.get("/deliveries/{pk}/status")
async def get_state(pk: str) -> Dict:
    state = redis.get(f"delivery:{pk}")
    if state:
        return json.loads(state)
    return {}


@app.post("/deliveries/create")
async def create_delivery(request: Request):
    body = await request.json()
    # Delivery
    delivery = Delivery(**body["data"]).save()
    # Event
    event = Event(
        delivery_id=delivery.pk,
        type=body["type"],
        data=json.dumps(body["data"]),
    ).save()
    # State
    state = consumers.CONSUMERS[event.type]({}, event)
    redis.set(f"delivery:{delivery.pk}", json.dumps(state))
    return state


@app.post("/event")
async def dispatch(request: Request):
    # Historical
    body = await request.json()
    delivery_id = body["delivery_id"]
    event = Event(
        delivery_id=delivery_id,
        type=body["type"],
        data=json.dumps(body["data"]),
    ).save()
    state = await get_state(delivery_id)
    # New state
    new_state = consumers.CONSUMERS[event.type](state, event)
    redis.set(f"delivery:{delivery_id}", json.dumps(new_state))
    return new_state
