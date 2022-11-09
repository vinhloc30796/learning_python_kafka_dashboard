from typing import Dict
import json

# Owned
from models import Event


def create_delivery(
    state: Dict,
    event: Event,
) -> Dict:
    """Create a delivery."""
    data = json.loads(event.data)
    return {
        "id": event.delivery_id,
        "budget": int(data["budget"]),
        "notes": data["notes"],
        "status": "ready",
    }


def start_delivery(
    state: Dict,
    event: Event,
) -> Dict:
    return state | { "status": "active" }


CONSUMERS = {
    "CREATE_DELIVERY": create_delivery,
    "START_DELIVERY": start_delivery,
}