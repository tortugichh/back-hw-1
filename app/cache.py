import redis
from app.config import settings

def get_redis_client():
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
        yield r
    except Exception as e:
        print(f"Could not connect to Redis: {e}")
        # Depending on your application's needs, you might want to raise an exception
        # or return a fallback (e.g., a mock Redis client or None)
        raise e
    finally:
        # In some cases, you might want to explicitly close the connection, but
        # redis-py's connection pooling generally handles this.
        pass 