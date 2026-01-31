# Tutorial: Building a Python Microservice with arch-mcp

Build a complete microservice using only Claude prompts with arch-mcp.

## Prerequisites

- Claude Code or Cursor with arch-mcp connected
- Python 3.11+

## Tech Stack (Auto-configured)

| Tool | Version | Purpose |
|------|---------|---------|
| FastAPI | 0.115.x | Web framework |
| Pydantic | 2.10.x | Data validation |
| pytest | 8.3.x | Testing |
| pytest-cov | 6.0.x | Coverage (80% min) |
| httpx | 0.28.x | Async HTTP client |
| structlog | 24.4.x | Structured logging |
| uvicorn | 0.34.x | ASGI server |
| ruff | 0.9.x | Linting |

---

## Step 1: Create the Project

> **Prompt:** "Create a new microservice called product-service"

This scaffolds a complete project with:
- FastAPI app with health endpoints
- Pydantic settings configuration
- Structured logging
- Pytest with 80% coverage requirement
- Base error classes
- `.arch-mcp/rules.yaml` for custom rules

**Follow the output instructions:**
```bash
cd product-service
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest  # Verify setup
```

---

## Step 2: Understand the Conventions

> **Prompt:** "What are the mandatory naming conventions?"

Key patterns:
| Type | Pattern | Example |
|------|---------|---------|
| Schemas | `{Resource}Create`, `{Resource}Response` | `ProductCreate` |
| Services | `{Resource}Service` | `ProductService` |
| Repositories | `{Resource}Repository` | `ProductRepository` |
| Errors | `{Resource}NotFoundError` | `ProductNotFoundError` |

---

## Step 3: Get the TDD Workflow

> **Prompt:** "Get the TDD workflow for implementing a product feature"

This explains the Red → Green → Refactor cycle:
1. Write failing tests first
2. Implement minimal code to pass
3. Refactor while keeping tests green

---

## Step 4: Add the Product Feature

> **Prompt:** "Add a product feature to my project"

This creates:
```
src/features/products/
├── __init__.py
├── schemas.py      # ProductCreate, ProductResponse
├── errors.py       # ProductNotFoundError
├── repository.py   # ProductRepository interface
├── service.py      # ProductService
└── router.py       # API endpoints

tests/features/products/
├── test_schemas.py
├── test_service.py
└── test_router.py
```

---

## Step 5: Register the Router

> **Prompt:** "How do I register the product router in main.py?"

Update `src/main.py`:
```python
from src.features.products import router as products_router

app.include_router(products_router)
```

---

## Step 6: Run Tests

```bash
pytest tests/features/products/ -v
```

All tests should pass - the scaffolded code follows TDD with tests already written.

---

## Step 7: Customize the Schema

> **Prompt:** "I need to add price and category fields to my product schema"

Update `src/features/products/schemas.py`:
```python
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: Decimal = Field(..., gt=0)
    category: str = Field(..., min_length=1)


class ProductResponse(BaseModel):
    id: str
    name: str
    price: Decimal
    category: str
    in_stock: bool = True

    model_config = {"from_attributes": True}
```

---

## Step 8: Add More Tests

> **Prompt:** "Generate test cases for product price validation"

Add to `tests/features/products/test_schemas.py`:
```python
def test_price_must_be_positive(self):
    from src.features.products.schemas import ProductCreate

    with pytest.raises(ValidationError):
        ProductCreate(name="Widget", price=-10, category="electronics")

def test_price_cannot_be_zero(self):
    from src.features.products.schemas import ProductCreate

    with pytest.raises(ValidationError):
        ProductCreate(name="Widget", price=0, category="electronics")
```

---

## Step 9: Validate Architecture

> **Prompt:** "Validate my products feature against architecture rules"

or

> **Prompt:** "Check my codebase for architecture violations"

This verifies:
- Naming conventions are followed
- No layer violations
- No security issues (hardcoded secrets, SQL injection)
- Proper error handling

---

## Step 10: Add Another Feature

> **Prompt:** "Add an order feature to my project"

Repeat the process for each feature. The MCP ensures consistency across all features.

---

## Step 11: Get Best Practices

> **Prompt:** "Show best practices for error-handling"

> **Prompt:** "Show best practices for security"

> **Prompt:** "Show best practices for testing"

---

## Step 12: Create Docker Setup

> **Prompt:** "Generate a Dockerfile for my microservice"

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

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
```

Create `.dockerignore`:
```
.git/
.venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
.ruff_cache/
.env
```

---

## Step 13: Create CI/CD

> **Prompt:** "Generate a GitHub Actions workflow for CI"

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

      - name: Lint
        run: ruff check src/ tests/

      - name: Test
        run: pytest --cov=src --cov-report=xml --cov-fail-under=80

  docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: docker build -t product-service .
```

---

## Quick Reference: All Prompts

| Task | Prompt |
|------|--------|
| Create project | "Create a new microservice called {name}" |
| Add feature | "Add a {feature} feature to my project" |
| Get conventions | "What are the mandatory naming conventions?" |
| Get TDD workflow | "Get the TDD workflow for implementing {feature}" |
| Generate template | "Generate a {type} template for {resource}" |
| Validate code | "Validate this code against architecture rules" |
| Check architecture | "Check my codebase for architecture violations" |
| Best practices | "Show best practices for {category}" |
| Project structure | "What's the recommended project structure?" |
| List rules | "List all {category} rules" |

---

## Summary

Everything is driven by prompts:

1. **"Create a new microservice called product-service"** → Full project
2. **"Add a product feature"** → Feature with tests
3. **"Validate my code"** → Architecture compliance
4. **"Show best practices for testing"** → Guidance

The MCP enforces:
- ✅ Consistent naming (`ProductService`, `ProductCreate`)
- ✅ TDD workflow (tests first)
- ✅ 80% coverage minimum
- ✅ Clean architecture (no layer violations)
- ✅ Security rules (no hardcoded secrets)
