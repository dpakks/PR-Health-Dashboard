import json
import redis
from app.config import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=settings.REDIS_DECODE_RESPONSES
)


def test_redis_connection():
    try:
        return redis_client.ping()
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False


def get_cache(key: str):
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Redis GET failed for key {key}: {e}")
        return None


def set_cache(key: str, value, expiry: int = 300):
    try:
        redis_client.setex(key, expiry, json.dumps(value, default=str))
    except Exception as e:
        print(f"Redis SET failed for key {key}: {e}")


def delete_cache(key: str):
    try:
        redis_client.delete(key)
    except Exception as e:
        print(f"Redis DELETE failed for key {key}: {e}")