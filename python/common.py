"""إعدادات وأدوات مشتركة بين كل سكريبتات المشروع."""
import os
import sqlite3

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DB_PATH = os.getenv("DB_PATH", "spam.db")
BLOOM_KEY = "spam:bloom"


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def get_db() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def random_number(rng) -> str:
    """رقم موبايل مصري عشوائي: 01[0|1|2|5] + 8 أرقام."""
    return f"01{rng.choice('0125')}{rng.randrange(10**8):08d}"
