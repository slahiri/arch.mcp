# Tutorial: Building a Python Microservice with arch-mcp

This guide walks through using arch-mcp to build a well-architected Python microservice for managing a product catalog using **Test-Driven Development (TDD)**.

## Setup

### Claude Code

```bash
# Remote (recommended)
claude mcp add arch-controls --url https://arch-mcp.sid.sh/sse

# Or local
claude mcp add arch-controls -- uvx arch-mcp
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "arch-controls": {
      "url": "https://arch-mcp.sid.sh/sse"
    }
  }
}
```

Restart your IDE after adding the configuration.

## Step 1: Get the Project Structure and Naming Conventions

Ask your AI assistant:

> "Get the naming conventions and clean-architecture project structure"

The MCP enforces these **mandatory** naming patterns:

| Type | Pattern | Example |
|------|---------|---------|
| Schemas | `{Resource}Create`, `{Resource}Response` | `ProductCreate`, `ProductResponse` |
| Services | `{Resource}Service` | `ProductService` |
| Repositories | `{Resource}Repository` | `ProductRepository` |
| Errors | `{Resource}NotFoundError` | `ProductNotFoundError` |
| Files | `{feature}_service.py`, `{feature}_router.py` | `product_service.py` |

Create the folder structure:

```bash
mkdir -p src/features/products tests/features/products
mkdir -p src/shared src/core
touch src/main.py src/core/config.py
```

## Step 2: Get the TDD Workflow

Ask your assistant:

> "Get the TDD workflow for implementing the product feature"

The MCP returns a step-by-step guide. TDD is **mandatory** - all code must be developed test-first:

```
Red → Green → Refactor
1. Write a failing test
2. Write minimal code to pass
3. Refactor while keeping tests green
```

## Step 3: Write Failing Tests for Schemas (RED)

Create `tests/features/products/test_schemas.py`:

```python
import pytest
from pydantic import ValidationError


def test_product_create_requires_name():
    """Test that ProductCreate requires a name field."""
    from src.features.products.schemas import ProductCreate

    with pytest.raises(ValidationError):
        ProductCreate(price=29.99, category="electronics")


def test_product_create_requires_positive_price():
    """Test that ProductCreate requires price > 0."""
    from src.features.products.schemas import ProductCreate

    with pytest.raises(ValidationError):
        ProductCreate(name="Widget", price=-10, category="electronics")


def test_product_create_valid():
    """Test valid ProductCreate schema."""
    from src.features.products.schemas import ProductCreate

    data = ProductCreate(name="Widget", price=29.99, category="electronics")
    assert data.name == "Widget"
    assert data.price == 29.99
```

Run the tests - they should **fail** (no schemas exist yet):

```bash
pytest tests/features/products/test_schemas.py -v
# Expected: ModuleNotFoundError
```

## Step 4: Implement Schemas to Pass Tests (GREEN)

Ask your assistant:

> "Generate a schemas template for product"

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


class ProductResponse(BaseModel):
    """Response schema for product."""
    id: str
    name: str
    price: Decimal
    category: str
    in_stock: bool = True

    model_config = {"from_attributes": True}
```

Run tests - they should **pass**:

```bash
pytest tests/features/products/test_schemas.py -v
# Expected: 3 passed
```

## Step 5: Write Failing Tests for Service (RED)

Create `tests/features/products/test_service.py`:

```python
import pytest
from unittest.mock import AsyncMock
from decimal import Decimal


@pytest.fixture
def mock_product_repository():
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


@pytest.mark.asyncio
async def test_create_product(mock_product_repository):
    """Test ProductService.create returns created entity."""
    from src.features.products.service import ProductService
    from src.features.products.schemas import ProductCreate

    service = ProductService(repository=mock_product_repository)
    data = ProductCreate(name="Widget", price=Decimal("29.99"), category="electronics")

    result = await service.create(data)

    assert result["id"] == "prod-123"
    assert result["name"] == "Widget"
    mock_product_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_get_product_not_found(mock_product_repository):
    """Test ProductService raises error when product not found."""
    from src.features.products.service import ProductService
    from src.features.products.errors import ProductNotFoundError

    service = ProductService(repository=mock_product_repository)

    with pytest.raises(ProductNotFoundError):
        await service.get_by_id("nonexistent")


@pytest.mark.asyncio
async def test_get_product_success(mock_product_repository):
    """Test ProductService returns product when found."""
    from src.features.products.service import ProductService

    mock_product_repository.get.return_value = {
        "id": "prod-123",
        "name": "Widget",
        "price": Decimal("29.99"),
        "category": "electronics",
    }

    service = ProductService(repository=mock_product_repository)
    result = await service.get_by_id("prod-123")

    assert result["id"] == "prod-123"
```

Run tests - they should **fail**:

```bash
pytest tests/features/products/test_service.py -v
# Expected: ModuleNotFoundError
```

## Step 6: Implement Service to Pass Tests (GREEN)

Create `src/features/products/errors.py`:

```python
"""Custom exceptions for products."""


class ProductError(Exception):
    """Base error for product operations."""
    pass


class ProductNotFoundError(ProductError):
    """Raised when product is not found."""
    def __init__(self, product_id: str):
        self.product_id = product_id
        super().__init__(f"Product '{product_id}' not found")


class ProductValidationError(ProductError):
    """Raised when product validation fails."""
    def __init__(self, message: str):
        super().__init__(message)
```

Create `src/features/products/repository.py`:

```python
"""Data access for products."""
from typing import Protocol


class ProductRepository(Protocol):
    """Repository interface for product persistence."""

    async def save(self, entity: dict) -> dict: ...
    async def get(self, id: str) -> dict | None: ...
    async def delete(self, id: str) -> bool: ...
    async def list_by_category(self, category: str) -> list[dict]: ...
```

Create `src/features/products/service.py`:

```python
"""Business logic for products."""
import logging
from .repository import ProductRepository
from .errors import ProductNotFoundError
from .schemas import ProductCreate

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, repository: ProductRepository):
        self._repository = repository

    async def create(self, data: ProductCreate) -> dict:
        logger.info("Creating product", extra={"name": data.name})
        entity = data.model_dump()
        return await self._repository.save(entity)

    async def get_by_id(self, product_id: str) -> dict:
        result = await self._repository.get(product_id)
        if not result:
            raise ProductNotFoundError(product_id)
        return result
```

Run tests - they should **pass**:

```bash
pytest tests/features/products/test_service.py -v
# Expected: 3 passed
```

## Step 7: Write Failing Tests for Router (RED)

Create `tests/features/products/test_router.py`:

```python
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_create_product_returns_201():
    """Test POST /products/ returns 201 with created entity."""
    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/products/",
            json={"name": "Widget", "price": 29.99, "category": "electronics"}
        )

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == "Widget"


@pytest.mark.asyncio
async def test_get_product_returns_404_when_not_found():
    """Test GET /products/{id} returns 404 when not found."""
    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/products/nonexistent")

    assert response.status_code == 404
```

## Step 8: Implement Router to Pass Tests (GREEN)

Create `src/features/products/router.py`:

```python
"""API routes for products."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from .schemas import ProductCreate, ProductResponse
from .service import ProductService
from .repository import ProductRepository
from .errors import ProductNotFoundError

router = APIRouter(prefix="/products", tags=["products"])


# In-memory implementation for demo
class InMemoryProductRepository:
    def __init__(self):
        self._products: dict[str, dict] = {}

    async def save(self, entity: dict) -> dict:
        product_id = str(uuid.uuid4())
        entity["id"] = product_id
        entity["in_stock"] = True
        self._products[product_id] = entity
        return entity

    async def get(self, id: str) -> dict | None:
        return self._products.get(id)

    async def delete(self, id: str) -> bool:
        if id in self._products:
            del self._products[id]
            return True
        return False

    async def list_by_category(self, category: str) -> list[dict]:
        return [p for p in self._products.values() if p["category"] == category]


# Dependency injection
_repository = InMemoryProductRepository()
_service = ProductService(_repository)


def get_product_service() -> ProductService:
    return _service


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    result = await service.create(data)
    return ProductResponse(**result)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    try:
        result = await service.get_by_id(product_id)
        return ProductResponse(**result)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail="Product not found")
```

Create `src/features/products/__init__.py`:

```python
from .router import router
```

Update `src/main.py`:

```python
"""Application entry point."""
import logging
from fastapi import FastAPI
from src.features.products import router as products_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="Product Catalog API")
app.include_router(products_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

Run all tests:

```bash
pytest tests/features/products/ -v
# Expected: All tests pass
```

## Step 9: Validate Architecture

Ask your assistant:

> "Check my architecture for layer violations and validate against naming conventions"

The MCP will verify:
- All files follow naming conventions
- No layer violations (service doesn't import from router)
- All classes use correct naming patterns
- Test coverage meets 80% minimum

## Step 10: Run with Coverage

```bash
pytest tests/features/products/ -v --cov=src/features/products --cov-report=term-missing --cov-fail-under=80
```

## Summary

This TDD workflow ensures:

| Step | Action | Tool Used |
|------|--------|-----------|
| 1 | Get naming conventions | `tool_get_naming_conventions` |
| 2 | Get TDD workflow | `tool_get_tdd_workflow` |
| 3 | Write failing test | Manual |
| 4 | Generate file template | `tool_get_file_template` |
| 5 | Implement to pass test | Manual |
| 6 | Validate code | `tool_validate_code` |
| 7 | Check architecture | `tool_check_architecture` |

The arch-mcp server enforces:

- **Mandatory naming** - `{Resource}Service`, `{Resource}Create`, etc.
- **Mandatory TDD** - Tests must be written first
- **80% coverage minimum** - Enforced via pytest-cov
- **Clean architecture** - Layer violations are errors
- **Standard structure** - Feature-based or clean-architecture patterns
