"""Database and cache layer for architecture rules."""

import json
import os
from datetime import datetime
from functools import lru_cache

import psycopg
import redis


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Environment variables
DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = os.environ.get("REDIS_URL", "")

# Cache TTL in seconds
CACHE_TTL = 300  # 5 minutes


@lru_cache
def get_redis_client() -> redis.Redis | None:
    """Get Redis client (singleton)."""
    if not REDIS_URL:
        return None
    return redis.from_url(REDIS_URL, decode_responses=True)


def get_db_connection():
    """Get PostgreSQL connection."""
    if not DATABASE_URL:
        return None
    return psycopg.connect(DATABASE_URL)


def cache_get(key: str) -> dict | list | None:
    """Get value from Redis cache."""
    client = get_redis_client()
    if not client:
        return None
    try:
        value = client.get(key)
        if value:
            return json.loads(value)
    except (redis.RedisError, json.JSONDecodeError):
        pass
    return None


def cache_set(key: str, value: dict | list, ttl: int = CACHE_TTL) -> None:
    """Set value in Redis cache."""
    client = get_redis_client()
    if not client:
        return
    try:
        client.setex(key, ttl, json.dumps(value, cls=DateTimeEncoder))
    except redis.RedisError:
        pass


def init_db() -> None:
    """Initialize database tables."""
    conn = get_db_connection()
    if not conn:
        return

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    name TEXT NOT NULL,
                    severity TEXT DEFAULT 'warning',
                    description TEXT,
                    pattern TEXT,
                    message TEXT,
                    fix TEXT,
                    example TEXT,
                    applies_to JSONB DEFAULT '["**/*.py"]',
                    exclude JSONB DEFAULT '[]',
                    best_practice BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS structures (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    structure TEXT,
                    layers JSONB DEFAULT '{}',
                    principles JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_rules_category ON rules(category)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_rules_severity ON rules(severity)
            """)
    conn.close()


def fetch_rules(category: str | None = None, severity: str | None = None) -> list[dict]:
    """Fetch rules from database with caching."""
    cache_key = f"rules:{category or 'all'}:{severity or 'all'}"

    # Try cache first
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    conn = get_db_connection()
    if not conn:
        return []

    query = "SELECT * FROM rules WHERE 1=1"
    params: list = []

    if category:
        query += " AND category = %s"
        params.append(category.lower())

    if severity:
        query += " AND severity = %s"
        params.append(severity.lower())

    with conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            rules = [dict(zip(columns, row)) for row in cur.fetchall()]

    conn.close()

    # Convert JSONB fields
    for rule in rules:
        if isinstance(rule.get("applies_to"), str):
            rule["applies_to"] = json.loads(rule["applies_to"])
        if isinstance(rule.get("exclude"), str):
            rule["exclude"] = json.loads(rule["exclude"])

    # Cache result
    cache_set(cache_key, rules)

    return rules


def fetch_rule(rule_id: str) -> dict | None:
    """Fetch a single rule by ID."""
    cache_key = f"rule:{rule_id}"

    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    conn = get_db_connection()
    if not conn:
        return None

    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rules WHERE id = %s", [rule_id])
            row = cur.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in cur.description]
            rule = dict(zip(columns, row))

    conn.close()

    # Convert JSONB fields
    if isinstance(rule.get("applies_to"), str):
        rule["applies_to"] = json.loads(rule["applies_to"])
    if isinstance(rule.get("exclude"), str):
        rule["exclude"] = json.loads(rule["exclude"])

    cache_set(cache_key, rule)

    return rule


def fetch_structures() -> dict[str, dict]:
    """Fetch all structures from database."""
    cache_key = "structures:all"

    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    conn = get_db_connection()
    if not conn:
        return {}

    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM structures")
            columns = [desc[0] for desc in cur.description]
            rows = [dict(zip(columns, row)) for row in cur.fetchall()]

    conn.close()

    structures = {}
    for row in rows:
        if isinstance(row.get("layers"), str):
            row["layers"] = json.loads(row["layers"])
        if isinstance(row.get("principles"), str):
            row["principles"] = json.loads(row["principles"])
        structures[row["id"]] = row

    cache_set(cache_key, structures)

    return structures


def fetch_structure(pattern: str) -> dict | None:
    """Fetch a single structure by pattern ID."""
    structures = fetch_structures()
    return structures.get(pattern)


def get_categories() -> list[str]:
    """Get all unique rule categories."""
    cache_key = "categories:all"

    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    conn = get_db_connection()
    if not conn:
        return []

    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT category FROM rules ORDER BY category")
            categories = [row[0] for row in cur.fetchall()]

    conn.close()

    cache_set(cache_key, categories)

    return categories


def seed_rules(rules: list[dict]) -> None:
    """Seed rules into the database."""
    conn = get_db_connection()
    if not conn:
        return

    with conn:
        with conn.cursor() as cur:
            for rule in rules:
                cur.execute("""
                    INSERT INTO rules (
                        id, category, name, severity, description, pattern,
                        message, fix, example, applies_to, exclude, best_practice
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        category = EXCLUDED.category,
                        name = EXCLUDED.name,
                        severity = EXCLUDED.severity,
                        description = EXCLUDED.description,
                        pattern = EXCLUDED.pattern,
                        message = EXCLUDED.message,
                        fix = EXCLUDED.fix,
                        example = EXCLUDED.example,
                        applies_to = EXCLUDED.applies_to,
                        exclude = EXCLUDED.exclude,
                        best_practice = EXCLUDED.best_practice,
                        updated_at = NOW()
                """, [
                    rule.get("id"),
                    rule.get("category"),
                    rule.get("name"),
                    rule.get("severity", "warning"),
                    rule.get("description"),
                    rule.get("pattern"),
                    rule.get("message"),
                    rule.get("fix"),
                    rule.get("example"),
                    json.dumps(rule.get("applies_to", ["**/*.py"])),
                    json.dumps(rule.get("exclude", [])),
                    rule.get("best_practice", False),
                ])
    conn.close()

    # Clear cache
    client = get_redis_client()
    if client:
        try:
            client.delete("rules:all:all", "categories:all")
        except redis.RedisError:
            pass


def seed_structures(structures: dict[str, dict]) -> None:
    """Seed structures into the database."""
    conn = get_db_connection()
    if not conn:
        return

    with conn:
        with conn.cursor() as cur:
            for sid, struct in structures.items():
                cur.execute("""
                    INSERT INTO structures (id, name, description, structure, layers, principles)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        structure = EXCLUDED.structure,
                        layers = EXCLUDED.layers,
                        principles = EXCLUDED.principles,
                        updated_at = NOW()
                """, [
                    sid,
                    struct.get("name"),
                    struct.get("description"),
                    struct.get("structure"),
                    json.dumps(struct.get("layers", {})),
                    json.dumps(struct.get("principles", [])),
                ])
    conn.close()

    # Clear cache
    client = get_redis_client()
    if client:
        try:
            client.delete("structures:all")
        except redis.RedisError:
            pass
