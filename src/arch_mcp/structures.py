"""Project structure templates for Python APIs"""

STRUCTURES = {
    "clean-architecture": {
        "name": "Clean Architecture",
        "description": "Layered architecture with clear separation of concerns",
        "structure": """
src/
├── api/                        # HTTP layer (FastAPI)
│   ├── routes/                 # Route handlers
│   ├── schemas/                # Pydantic request/response models
│   ├── dependencies.py         # FastAPI dependencies (DI)
│   └── middleware.py
├── application/                # Business logic
│   ├── services/               # Application services
│   └── interfaces/             # Protocols/ABCs
├── domain/                     # Core (no dependencies)
│   ├── entities/               # Domain models
│   └── errors.py               # Domain exceptions
├── infrastructure/             # External concerns
│   ├── database/               # SQLAlchemy setup
│   └── repositories/           # Repository implementations
├── core/                       # Config & cross-cutting
│   └── config.py               # Pydantic settings
└── main.py""",
        "layers": {
            "api": {
                "can_import": ["application", "domain", "core"],
                "cannot_import": ["infrastructure"],
            },
            "application": {
                "can_import": ["domain", "core"],
                "cannot_import": ["api", "infrastructure"],
            },
            "domain": {
                "can_import": [],
                "cannot_import": ["api", "application", "infrastructure", "core"],
            },
            "infrastructure": {
                "can_import": ["domain", "application", "core"],
                "cannot_import": ["api"],
            },
        },
        "principles": [
            "Dependencies point inward: infrastructure → application → domain",
            "Domain layer has NO external dependencies",
            "Use Protocols/ABCs for interfaces at boundaries",
            "Dependency injection via FastAPI Depends",
        ],
    },
    "feature-based": {
        "name": "Feature-Based (Modular)",
        "description": "Organize by feature/domain for better scalability",
        "structure": """
src/
├── features/
│   ├── users/
│   │   ├── router.py           # FastAPI router
│   │   ├── schemas.py          # Pydantic models
│   │   ├── service.py          # Business logic
│   │   ├── repository.py       # Data access
│   │   └── models.py           # SQLAlchemy models
│   ├── auth/
│   │   └── ...
│   └── orders/
│       └── ...
├── shared/                     # Shared across features
│   ├── database.py
│   ├── schemas.py              # Common schemas
│   └── errors.py
├── core/
│   └── config.py
└── main.py""",
        "layers": {
            "features": {"can_import": ["shared", "core"], "cannot_import": []},
            "shared": {"can_import": ["core"], "cannot_import": ["features"]},
        },
        "principles": [
            "Each feature is self-contained",
            "Shared code lives in shared/",
            "Features can ONLY import from shared/ (not other features)",
            "Easy to extract features into microservices later",
        ],
    },
    "simple": {
        "name": "Simple (Small APIs)",
        "description": "Minimal structure for small APIs or MVPs",
        "structure": """
src/
├── main.py                     # FastAPI app + routes
├── config.py                   # Pydantic settings
├── database.py                 # DB connection
├── models.py                   # SQLAlchemy models
├── schemas.py                  # Pydantic schemas
├── services.py                 # Business logic
└── errors.py                   # Custom exceptions

tests/
├── conftest.py                 # Fixtures
└── test_api.py                 # API tests""",
        "layers": {},
        "principles": [
            "Good for small APIs (< 10 endpoints)",
            "All in one place, easy to understand",
            "Migrate to feature-based when it grows",
        ],
    },
}
