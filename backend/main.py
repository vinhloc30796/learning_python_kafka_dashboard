# Base
import json

# Server
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Owned
import consumers
from models import Event, Delivery

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/deliveries/create")
async def create_delivery(request: Request):
    body = await request.json()
    #  Delivery
    delivery = Delivery(**body["data"]).save()
    # Event
    event = Event(
        delivery_id=delivery.pk,
        type=body["type"],
        data=json.dumps(body["data"]),
    ).save()
    # State
    state = consumers.create_delivery({}, event)
    return state
