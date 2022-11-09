from typing import Dict
import json

# Owned
from models import Event


def create_delivery(
    state: Dict,
    event: Event,
) -> None:
    """Create a delivery."""
    data = json.loads(event.data)
    return {
        "id": event.delivery_id,
        "budget": int(data["budget"]),
        "notes": data["notes"],
        "status": "ready",
    }