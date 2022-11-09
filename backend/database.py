# Base
import os

# Database
from redis_om import get_redis_connection

redis = get_redis_connection(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=os.getenv("REDIS_PORT", 14698),
    password=os.getenv("REDIS_PASS", "password"),
    decode_responses=True,
)