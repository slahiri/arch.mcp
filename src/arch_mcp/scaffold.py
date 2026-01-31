#!/usr/bin/env python3
"""Scaffold a new Python microservice following arch-mcp conventions."""

import argparse
from pathlib import Path


def create_file(path: Path, content: str) -> None:
    """Create a file with content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  Created: {path}")


def scaffold_project(name: str, base_dir: Path) -> None:
    """Scaffold a new microservice project."""
    project_dir = base_dir / name

    if project_dir.exists():
        print(f"Error: Directory '{project_dir}' already exists")
        return

    print(f"\nScaffolding microservice: {name}")
    print("=" * 50)

    # pyproject.toml
    create_file(project_dir / "pyproject.toml", f'''[project]
name = "{name}"
version = "0.1.0"
description = "A Python microservice"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "structlog>=24.1.0",
    "httpx>=0.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=4.1",
    "ruff>=0.8.0",
    "httpx>=0.26.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --cov=src --cov-report=term-missing --cov-fail-under=80"
''')

    # .gitignore
    create_file(project_dir / ".gitignore", '''__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
.env
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.ruff_cache/
.mypy_cache/
''')

    # README
    create_file(project_dir / "README.md", f'''# {name}

A Python microservice built with FastAPI following clean architecture.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
uvicorn src.main:app --reload
```

## Test (TDD)

```bash
# Run all tests with coverage
pytest

# Run specific feature tests
pytest tests/features/{{feature}}/ -v

# Watch mode
pytest-watch
```

## Architecture

```
src/
├── core/           # Configuration
├── shared/         # Shared utilities
├── features/       # Feature modules
│   └── {{feature}}/
│       ├── router.py
│       ├── schemas.py
│       ├── service.py
│       ├── repository.py
│       └── errors.py
└── main.py
```
''')

    # Main application
    create_file(project_dir / "src" / "main.py", '''"""Application entry point."""
import structlog
from fastapi import FastAPI

from src.core.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.on_event("startup")
async def startup():
    logger.info("application_started", app=settings.app_name)
''')

    # Core config
    create_file(project_dir / "src" / "core" / "__init__.py", "")
    create_file(
        project_dir / "src" / "core" / "config.py",
        f'''"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "{name}"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./app.db"

    # Add more settings as needed

    model_config = {{"env_file": ".env", "extra": "ignore"}}


settings = Settings()
''')

    # Shared utilities
    create_file(project_dir / "src" / "shared" / "__init__.py", "")
    create_file(
        project_dir / "src" / "shared" / "errors.py",
        '''"""Base error classes for the application."""


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found error."""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} '{resource_id}' not found",
            code="NOT_FOUND",
            status_code=404,
        )


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
        )
''')

    create_file(project_dir / "src" / "shared" / "schemas.py", '''"""Shared Pydantic schemas."""
from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
''')

    # Features placeholder
    create_file(project_dir / "src" / "features" / "__init__.py", "")

    # Example feature: health (minimal)
    create_file(
        project_dir / "src" / "features" / "health" / "__init__.py",
        "from .router import router",
    )
    create_file(
        project_dir / "src" / "features" / "health" / "router.py",
        '''"""Health check router."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/ready")
async def readiness():
    """Readiness probe."""
    return {"status": "ready"}


@router.get("/live")
async def liveness():
    """Liveness probe."""
    return {"status": "live"}
''')

    # Tests
    create_file(project_dir / "tests" / "__init__.py", "")
    create_file(project_dir / "tests" / "conftest.py", '''"""Pytest fixtures."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client():
    """Async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
''')

    create_file(project_dir / "tests" / "test_health.py", '''"""Health endpoint tests."""
import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    """Test health endpoint returns ok status."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_returns_ready(client):
    """Test readiness probe returns ready."""
    response = await client.get("/api/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
''')

    # .env.example
    create_file(project_dir / ".env.example", f'''# Application
APP_NAME={name}
DEBUG=false

# Database
DATABASE_URL=sqlite:///./app.db
''')

    # arch-mcp rules (copy from package or create minimal)
    create_file(
        project_dir / ".arch-mcp" / "rules.yaml",
        '''# Custom architecture rules for this project
# Inherits from arch-mcp defaults, add project-specific rules here

# Example: Add a custom rule
# security:
#   - id: custom-auth-required
#     name: All endpoints require auth
#     severity: error
#     pattern: "@router\\.(get|post).*\\n(?!.*Depends.*get_current_user)"
#     applies_to: ["**/router.py"]
''')

    print("\n" + "=" * 50)
    print(f"✓ Project scaffolded at: {project_dir}")
    print("\nNext steps:")
    print(f"  cd {name}")
    print("  python -m venv .venv")
    print("  source .venv/bin/activate")
    print("  pip install -e '.[dev]'")
    print("  pytest  # Run tests")
    print("  uvicorn src.main:app --reload  # Start server")
    print("\nTo add a new feature, ask Claude:")
    print('  "Generate a service template for users"')
    print('  "Get the TDD workflow for implementing users"')


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new Python microservice"
    )
    parser.add_argument("name", help="Project name (e.g., user-service)")
    parser.add_argument(
        "--dir",
        default=".",
        help="Base directory (default: current)"
    )

    args = parser.parse_args()
    scaffold_project(args.name, Path(args.dir))


if __name__ == "__main__":
    main()
