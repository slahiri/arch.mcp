# Tutorial: Building a Python Microservice with arch-mcp

This tutorial walks you through building a production-ready Python microservice using arch-mcp to enforce architecture standards and TDD practices.

## Prerequisites

- Python 3.11+
- Claude Code or Cursor with arch-mcp connected

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| FastAPI | 0.115.x | Web framework |
| Pydantic | 2.10.x | Data validation |
| SQLAlchemy | 2.0.x | ORM |
| Alembic | 1.14.x | Database migrations |
| pytest | 8.3.x | Testing |
| pytest-cov | 6.0.x | Coverage reporting |
| pytest-asyncio | 0.25.x | Async test support |
| httpx | 0.28.x | Async HTTP client for tests |
| structlog | 24.4.x | Structured logging |
| uvicorn | 0.34.x | ASGI server |
| ruff | 0.9.x | Linting |
| Docker | 24.x+ | Containerization |

---

## Part 1: Project Setup

### Step 1: Scaffold the Project

```bash
# Install arch-mcp
pip install arch-mcp

# Create new project
arch-mcp-scaffold product-service
cd product-service

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Step 2: Verify Setup

```bash
# Run tests (should pass)
pytest

# Start server
uvicorn src.main:app --reload

# Test health endpoint
curl http://localhost:8000/health
```

---

## Part 2: Add a Feature Using TDD

We'll add a **products** feature following Test-Driven Development.

### Step 3: Get the TDD Workflow

Ask Claude:

> **Prompt:** "Get the TDD workflow for implementing a product feature"

This returns the step-by-step TDD process we'll follow.

### Step 4: Get Naming Conventions

Ask Claude:

> **Prompt:** "What are the mandatory naming conventions?"

Key conventions:
- Schemas: `ProductCreate`, `ProductResponse`
- Service: `ProductService`
- Repository: `ProductRepository`
- Errors: `ProductNotFoundError`
- Files: `product_service.py`, `product_router.py`

---

## Part 3: Write Failing Tests First (RED)

### Step 5: Create Schema Tests

Create `tests/features/products/test_schemas.py`:

```python
"""Tests for product schemas - written BEFORE implementation."""
import pytest
from pydantic import ValidationError


class TestProductCreate:
    """Tests for ProductCreate schema."""

    def test_valid_product(self):
        """Test creating a valid product."""
        from src.features.products.schemas import ProductCreate

        product = ProductCreate(
            name="Widget",
            price=29.99,
            category="electronics",
        )
        assert product.name == "Widget"
        assert product.price == 29.99

    def test_name_required(self):
        """Test that name is required."""
        from src.features.products.schemas import ProductCreate

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(price=29.99, category="electronics")
        assert "name" in str(exc_info.value)

    def test_price_must_be_positive(self):
        """Test that price must be greater than 0."""
        from src.features.products.schemas import ProductCreate

        with pytest.raises(ValidationError):
            ProductCreate(name="Widget", price=-10, category="electronics")

    def test_price_must_be_positive_zero(self):
        """Test that price cannot be zero."""
        from src.features.products.schemas import ProductCreate

        with pytest.raises(ValidationError):
            ProductCreate(name="Widget", price=0, category="electronics")


class TestProductResponse:
    """Tests for ProductResponse schema."""

    def test_includes_id(self):
        """Test that response includes id."""
        from src.features.products.schemas import ProductResponse

        product = ProductResponse(
            id="prod-123",
            name="Widget",
            price=29.99,
            category="electronics",
            in_stock=True,
        )
        assert product.id == "prod-123"
```

Run tests (they should FAIL - schemas don't exist yet):

```bash
pytest tests/features/products/test_schemas.py -v
# Expected: ModuleNotFoundError
```

### Step 6: Create Service Tests

Create `tests/features/products/test_service.py`:

```python
"""Tests for ProductService - written BEFORE implementation."""
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock


@pytest.fixture
def mock_repository():
    """Mock product repository."""
    repo = AsyncMock()
    repo.save.return_value = {
        "id": "prod-123",
        "name": "Widget",
        "price": Decimal("29.99"),
        "category": "electronics",
        "in_stock": True,
    }
    repo.get.return_value = None  # Default: not found
    return repo


class TestProductServiceCreate:
    """Tests for ProductService.create method."""

    @pytest.mark.asyncio
    async def test_create_returns_product_with_id(self, mock_repository):
        """Test that create returns product with generated id."""
        from src.features.products.service import ProductService
        from src.features.products.schemas import ProductCreate

        service = ProductService(repository=mock_repository)
        data = ProductCreate(name="Widget", price=Decimal("29.99"), category="electronics")

        result = await service.create(data)

        assert result["id"] == "prod-123"
        assert result["name"] == "Widget"
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_sets_in_stock_true(self, mock_repository):
        """Test that new products are in stock by default."""
        from src.features.products.service import ProductService
        from src.features.products.schemas import ProductCreate

        service = ProductService(repository=mock_repository)
        data = ProductCreate(name="Widget", price=Decimal("29.99"), category="electronics")

        result = await service.create(data)

        assert result["in_stock"] is True


class TestProductServiceGetById:
    """Tests for ProductService.get_by_id method."""

    @pytest.mark.asyncio
    async def test_get_returns_product_when_found(self, mock_repository):
        """Test that get_by_id returns product when it exists."""
        from src.features.products.service import ProductService

        mock_repository.get.return_value = {
            "id": "prod-123",
            "name": "Widget",
            "price": Decimal("29.99"),
            "category": "electronics",
            "in_stock": True,
        }

        service = ProductService(repository=mock_repository)
        result = await service.get_by_id("prod-123")

        assert result["id"] == "prod-123"
        mock_repository.get.assert_called_once_with("prod-123")

    @pytest.mark.asyncio
    async def test_get_raises_not_found_error(self, mock_repository):
        """Test that get_by_id raises error when product not found."""
        from src.features.products.service import ProductService
        from src.features.products.errors import ProductNotFoundError

        mock_repository.get.return_value = None

        service = ProductService(repository=mock_repository)

        with pytest.raises(ProductNotFoundError) as exc_info:
            await service.get_by_id("nonexistent")

        assert "nonexistent" in str(exc_info.value)
```

### Step 7: Create Router Tests

Create `tests/features/products/test_router.py`:

```python
"""Tests for product API endpoints - written BEFORE implementation."""
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    """Async HTTP client for testing."""
    from src.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


class TestCreateProduct:
    """Tests for POST /api/products endpoint."""

    @pytest.mark.asyncio
    async def test_create_product_returns_201(self, client):
        """Test successful product creation returns 201."""
        response = await client.post(
            "/api/products/",
            json={"name": "Widget", "price": 29.99, "category": "electronics"},
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Widget"

    @pytest.mark.asyncio
    async def test_create_product_invalid_price(self, client):
        """Test that negative price returns 422."""
        response = await client.post(
            "/api/products/",
            json={"name": "Widget", "price": -10, "category": "electronics"},
        )

        assert response.status_code == 422


class TestGetProduct:
    """Tests for GET /api/products/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, client):
        """Test that missing product returns 404."""
        response = await client.get("/api/products/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
```

Create test directory structure:

```bash
mkdir -p tests/features/products
touch tests/features/products/__init__.py
```

---

## Part 4: Implement to Pass Tests (GREEN)

### Step 8: Generate Templates

Ask Claude:

> **Prompt:** "Generate a schemas template for product"

Create `src/features/products/schemas.py`:

```python
"""Pydantic schemas for products."""
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """Request schema for creating a product."""

    name: str = Field(..., min_length=1, max_length=200)
    price: Decimal = Field(..., gt=0)
    category: str = Field(..., min_length=1)


class ProductUpdate(BaseModel):
    """Request schema for updating a product."""

    name: str | None = Field(None, min_length=1, max_length=200)
    price: Decimal | None = Field(None, gt=0)
    category: str | None = None
    in_stock: bool | None = None


class ProductResponse(BaseModel):
    """Response schema for product."""

    id: str
    name: str
    price: Decimal
    category: str
    in_stock: bool = True

    model_config = {"from_attributes": True}
```

Run schema tests:

```bash
pytest tests/features/products/test_schemas.py -v
# Expected: All pass
```

### Step 9: Create Errors

Create `src/features/products/errors.py`:

```python
"""Custom exceptions for products."""
from src.shared.errors import AppError


class ProductError(AppError):
    """Base error for product operations."""

    pass


class ProductNotFoundError(ProductError):
    """Raised when product is not found."""

    def __init__(self, product_id: str):
        self.product_id = product_id
        super().__init__(
            message=f"Product '{product_id}' not found",
            code="PRODUCT_NOT_FOUND",
            status_code=404,
        )


class ProductValidationError(ProductError):
    """Raised when product validation fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="PRODUCT_VALIDATION_ERROR",
            status_code=400,
        )
```

### Step 10: Create Repository

Create `src/features/products/repository.py`:

```python
"""Data access for products."""
import uuid
from typing import Protocol


class ProductRepository(Protocol):
    """Repository interface for product persistence."""

    async def save(self, entity: dict) -> dict:
        """Save a product and return it with generated id."""
        ...

    async def get(self, product_id: str) -> dict | None:
        """Get a product by id, returns None if not found."""
        ...

    async def delete(self, product_id: str) -> bool:
        """Delete a product, returns True if deleted."""
        ...

    async def list_by_category(self, category: str) -> list[dict]:
        """List all products in a category."""
        ...


class InMemoryProductRepository:
    """In-memory implementation for development/testing."""

    def __init__(self):
        self._products: dict[str, dict] = {}

    async def save(self, entity: dict) -> dict:
        """Save a product."""
        product_id = str(uuid.uuid4())
        product = {
            "id": product_id,
            **entity,
            "in_stock": entity.get("in_stock", True),
        }
        self._products[product_id] = product
        return product

    async def get(self, product_id: str) -> dict | None:
        """Get a product by id."""
        return self._products.get(product_id)

    async def delete(self, product_id: str) -> bool:
        """Delete a product."""
        if product_id in self._products:
            del self._products[product_id]
            return True
        return False

    async def list_by_category(self, category: str) -> list[dict]:
        """List products by category."""
        return [p for p in self._products.values() if p["category"] == category]
```

### Step 11: Create Service

Create `src/features/products/service.py`:

```python
"""Business logic for products."""
import structlog

from .errors import ProductNotFoundError
from .repository import ProductRepository
from .schemas import ProductCreate

logger = structlog.get_logger()


class ProductService:
    """Service for product operations."""

    def __init__(self, repository: ProductRepository):
        self._repository = repository

    async def create(self, data: ProductCreate) -> dict:
        """Create a new product."""
        logger.info("creating_product", name=data.name, category=data.category)

        entity = data.model_dump()
        entity["in_stock"] = True

        product = await self._repository.save(entity)

        logger.info("product_created", product_id=product["id"])
        return product

    async def get_by_id(self, product_id: str) -> dict:
        """Get a product by id."""
        product = await self._repository.get(product_id)

        if not product:
            logger.warning("product_not_found", product_id=product_id)
            raise ProductNotFoundError(product_id)

        return product

    async def list_by_category(self, category: str) -> list[dict]:
        """List products by category."""
        return await self._repository.list_by_category(category)
```

Run service tests:

```bash
pytest tests/features/products/test_service.py -v
# Expected: All pass
```

### Step 12: Create Router

Create `src/features/products/router.py`:

```python
"""API routes for products."""
from fastapi import APIRouter, Depends, HTTPException, status

from .errors import ProductNotFoundError
from .repository import InMemoryProductRepository, ProductRepository
from .schemas import ProductCreate, ProductResponse
from .service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])

# Dependency injection
_repository = InMemoryProductRepository()


def get_repository() -> ProductRepository:
    """Get product repository."""
    return _repository


def get_product_service(
    repository: ProductRepository = Depends(get_repository),
) -> ProductService:
    """Get product service."""
    return ProductService(repository=repository)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Create a new product."""
    result = await service.create(data)
    return ProductResponse(**result)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Get a product by id."""
    try:
        result = await service.get_by_id(product_id)
        return ProductResponse(**result)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
```

### Step 13: Create Feature Init

Create `src/features/products/__init__.py`:

```python
"""Products feature module."""
from .router import router

__all__ = ["router"]
```

### Step 14: Register Router

Update `src/main.py`:

```python
"""Application entry point."""
import structlog
from fastapi import FastAPI

from src.core.config import settings
from src.features.health import router as health_router
from src.features.products import router as products_router

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

# Register routers
app.include_router(health_router)
app.include_router(products_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.on_event("startup")
async def startup():
    logger.info("application_started", app=settings.app_name)
```

### Step 15: Run All Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing

# Expected output:
# ==================== 15+ passed ====================
# TOTAL    XXX    XX    80%+
```

---

## Part 5: Validate Architecture

### Step 16: Check Architecture Rules

Ask Claude:

> **Prompt:** "Validate my products feature against architecture rules"

Or check the entire codebase:

> **Prompt:** "Check my codebase for architecture violations"

---

## Part 6: Docker Setup

### Step 17: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install dependencies first (for caching)
COPY pyproject.toml .
RUN pip install .

# Copy application code
COPY src/ src/

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 18: Create Docker Compose

Create `docker-compose.yml`:

```yaml
version: "3.9"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_NAME=product-service
      - DEBUG=false
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Add database when needed
  # db:
  #   image: postgres:16-alpine
  #   environment:
  #     POSTGRES_USER: app
  #     POSTGRES_PASSWORD: secret
  #     POSTGRES_DB: products
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data

# volumes:
#   postgres_data:
```

### Step 19: Create .dockerignore

Create `.dockerignore`:

```
.git/
.venv/
venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/
.ruff_cache/
.env
*.egg-info/
dist/
build/
.DS_Store
```

### Step 20: Build and Run

```bash
# Build image
docker build -t product-service .

# Run container
docker run -p 8000:8000 product-service

# Or use docker compose
docker compose up --build
```

---

## Part 7: CI/CD Setup

### Step 21: Create GitHub Actions

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint with ruff
        run: ruff check src/ tests/

      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml

  docker:
    runs-on: ubuntu-latest
    needs: test

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t product-service .

      - name: Run container tests
        run: |
          docker run -d -p 8000:8000 --name test-container product-service
          sleep 5
          curl -f http://localhost:8000/health
          docker stop test-container
```

---

## Summary

You've built a production-ready microservice with:

| Component | Implementation |
|-----------|----------------|
| **Architecture** | Feature-based clean architecture |
| **API Framework** | FastAPI with dependency injection |
| **Validation** | Pydantic schemas with constraints |
| **Testing** | pytest with 80%+ coverage |
| **Logging** | Structured logging with structlog |
| **Containerization** | Docker with health checks |
| **CI/CD** | GitHub Actions with lint, test, build |

### arch-mcp Tools Used

| Step | Tool | Purpose |
|------|------|---------|
| 3 | `tool_get_tdd_workflow` | Get TDD steps |
| 4 | `tool_get_naming_conventions` | Naming standards |
| 8 | `tool_get_file_template` | Generate schemas |
| 16 | `tool_validate_code` | Check rules |
| 16 | `tool_check_architecture` | Verify layers |

### Next Steps

1. Add database persistence (SQLAlchemy + Alembic)
2. Add authentication (JWT)
3. Add more features using TDD
4. Deploy to cloud (Railway, Fly.io, AWS)

Ask Claude:
> "Get the TDD workflow for implementing user authentication"
