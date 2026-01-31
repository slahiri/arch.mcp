"""Project structure templates for Python APIs"""

# Opinionated naming conventions - these are MANDATORY
NAMING_CONVENTIONS = {
    "files": {
        "routers": "{feature}_router.py or router.py",
        "schemas": "{feature}_schemas.py or schemas.py",
        "services": "{feature}_service.py or service.py",
        "repositories": "{feature}_repository.py or repository.py",
        "models": "{feature}_models.py or models.py",
        "errors": "errors.py (per feature or shared)",
        "config": "config.py (only in core/)",
        "tests": "test_{module}.py",
    },
    "classes": {
        "schemas_request": "{Resource}Create, {Resource}Update, {Resource}Patch",
        "schemas_response": "{Resource}Response, {Resource}List",
        "services": "{Resource}Service",
        "repositories": "{Resource}Repository",
        "errors": "{Resource}NotFoundError, {Resource}ValidationError",
        "models": "{Resource} (singular, PascalCase)",
    },
    "functions": {
        "router_endpoints": (
            "create_{resource}, get_{resource}, list_{resources}, "
            "update_{resource}, delete_{resource}"
        ),
        "service_methods": "create, get_by_id, list, update, delete, find_by_{field}",
        "repository_methods": "save, get, find_by_{field}, delete, exists",
    },
    "variables": {
        "style": "snake_case for all variables and functions",
        "private": "_prefix for internal/private attributes",
        "constants": "UPPER_SNAKE_CASE",
    },
}

# Standard file templates
FILE_TEMPLATES = {
    "router": '''"""API routes for {feature}."""
from fastapi import APIRouter, Depends, HTTPException, status

from .schemas import {Resource}Create, {Resource}Response
from .service import {Resource}Service

router = APIRouter(prefix="/{resources}", tags=["{resources}"])


def get_service() -> {Resource}Service:
    # Wire up dependencies here
    ...


@router.post("/", response_model={Resource}Response, status_code=status.HTTP_201_CREATED)
async def create_{resource}(
    data: {Resource}Create,
    service: {Resource}Service = Depends(get_service),
) -> {Resource}Response:
    return await service.create(data)


@router.get("/{{id}}", response_model={Resource}Response)
async def get_{resource}(
    id: str,
    service: {Resource}Service = Depends(get_service),
) -> {Resource}Response:
    result = await service.get_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    return result
''',
    "schemas": '''"""Pydantic schemas for {feature}."""
from pydantic import BaseModel, Field


class {Resource}Create(BaseModel):
    """Request schema for creating a {resource}."""
    name: str = Field(..., min_length=1, max_length=200)


class {Resource}Update(BaseModel):
    """Request schema for updating a {resource}."""
    name: str | None = Field(None, min_length=1, max_length=200)


class {Resource}Response(BaseModel):
    """Response schema for {resource}."""
    id: str
    name: str

    model_config = {{"from_attributes": True}}
''',
    "service": '''"""Business logic for {feature}."""
import logging
from .repository import {Resource}Repository
from .errors import {Resource}NotFoundError

logger = logging.getLogger(__name__)


class {Resource}Service:
    def __init__(self, repository: {Resource}Repository):
        self._repository = repository

    async def create(self, data) -> ...:
        logger.info("Creating {resource}", extra={{"data": data.model_dump()}})
        return await self._repository.save(data)

    async def get_by_id(self, id: str) -> ...:
        result = await self._repository.get(id)
        if not result:
            raise {Resource}NotFoundError(id)
        return result
''',
    "repository": '''"""Data access for {feature}."""
from typing import Protocol


class {Resource}Repository(Protocol):
    """Repository interface for {resource} persistence."""

    async def save(self, entity) -> ...: ...
    async def get(self, id: str) -> ... | None: ...
    async def delete(self, id: str) -> bool: ...
    async def exists(self, id: str) -> bool: ...
''',
    "errors": '''"""Custom exceptions for {feature}."""


class {Resource}Error(Exception):
    """Base error for {resource} operations."""
    pass


class {Resource}NotFoundError({Resource}Error):
    """Raised when {resource} is not found."""
    def __init__(self, id: str):
        self.id = id
        super().__init__(f"{Resource} '{{id}}' not found")


class {Resource}ValidationError({Resource}Error):
    """Raised when {resource} validation fails."""
    def __init__(self, message: str):
        super().__init__(message)
''',
}

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
