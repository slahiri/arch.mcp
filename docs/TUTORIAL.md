# Tutorial: Build a Microservice with Claude Prompts

Build a complete Python microservice using only Claude prompts.

## Prerequisites

- Claude Code with arch-mcp connected
- Python 3.11+

```bash
claude mcp add --transport sse arch-controls https://arch-mcp.sid.sh/sse
```

---

## Part 1: Create the Project

### Prompt 1: Scaffold Project

> **"Create a new microservice called product-service"**

Output:
```
✓ Project scaffolded at: product-service

Next steps:
  cd product-service
  python -m venv .venv
  source .venv/bin/activate
  pip install -e '.[dev]'
  pytest
```

### Setup

```bash
cd product-service
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest  # Should pass
```

### What You Get

```
product-service/
├── src/
│   ├── main.py              # FastAPI app
│   ├── core/
│   │   └── config.py        # Pydantic settings
│   ├── shared/
│   │   ├── errors.py        # Base exceptions
│   │   └── schemas.py       # Shared schemas
│   └── features/
│       └── health/          # Health endpoints
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   └── test_health.py       # Health tests
├── pyproject.toml           # Dependencies
├── .gitignore
└── .arch-mcp/
    └── rules.yaml           # Custom rules
```

---

## Part 2: Understand the Rules

### Prompt 2: Get Naming Conventions

> **"What are the naming conventions?"**

Output:
```
Mandatory naming patterns:

Classes:
  - Schemas: {Resource}Create, {Resource}Response
  - Services: {Resource}Service
  - Repositories: {Resource}Repository
  - Errors: {Resource}NotFoundError

Files:
  - product_service.py
  - product_router.py
  - product_schemas.py
```

### Prompt 3: Get Project Structure

> **"What's the recommended project structure?"**

Shows clean-architecture, feature-based, or simple patterns.

---

## Part 3: Add a Feature

### Prompt 4: Scaffold Feature

> **"Add a product feature to my project"**

Output:
```
✓ Feature 'product' scaffolded

Files created:
  - src/features/product/schemas.py
  - src/features/product/errors.py
  - src/features/product/repository.py
  - src/features/product/service.py
  - src/features/product/router.py
  - tests/features/product/test_schemas.py
  - tests/features/product/test_service.py
  - tests/features/product/test_router.py

Next steps:
  1. Add router to src/main.py
  2. Run: pytest tests/features/product/ -v
```

### Register the Router

Update `src/main.py`:

```python
from src.features.product import router as product_router

app.include_router(product_router)
```

### Run Tests

```bash
pytest tests/features/product/ -v
# All tests pass - TDD structure already in place
```

---

## Part 4: Customize the Feature

### Prompt 5: Get TDD Workflow

> **"Get the TDD workflow for implementing product"**

Shows:
1. Write failing test
2. Implement to pass
3. Refactor

### Add Fields to Schema

Edit `src/features/product/schemas.py`:

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

### Add Tests for New Fields

Add to `tests/features/product/test_schemas.py`:

```python
def test_price_must_be_positive(self):
    from src.features.product.schemas import ProductCreate

    with pytest.raises(ValidationError):
        ProductCreate(name="Test", price=-10, category="electronics")
```

---

## Part 5: Validate Your Code

### Prompt 6: Validate Code

> **"Validate my product feature against architecture rules"**

Or paste specific code:

> **"Validate this code:**
> ```python
> def get_user():
>     try:
>         return db.query()
>     except:
>         pass
> ```
> **"**

Output:
```
Violations:
  - no-bare-except (error): Don't use bare 'except:'
    Line 4: except:
    Fix: Catch specific exceptions
```

### Prompt 7: Check Full Architecture

> **"Check my codebase for architecture violations"**

Checks:
- Layer violations (domain importing infrastructure)
- Naming convention violations
- Security issues

---

## Part 6: Add More Features

### Prompt 8: Add Another Feature

> **"Add an order feature to my project"**

Same structure, consistent patterns.

### Prompt 9: Best Practices

> **"Show best practices for error-handling"**

> **"Show best practices for testing"**

> **"Show best practices for security"**

---

## Part 7: Production Setup

### Prompt 10: Docker Setup

> **"How should I containerize this service?"**

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ src/

RUN adduser --disabled-password appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_NAME=product-service
```

Create `.dockerignore`:

```
.git/
.venv/
__pycache__/
.pytest_cache/
.coverage
.env
```

### Build & Run

```bash
docker compose up --build
curl http://localhost:8000/health
```

---

## Part 8: CI/CD

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - run: pip install -e ".[dev]"
      - run: ruff check src/ tests/
      - run: pytest --cov=src --cov-fail-under=80

  docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t product-service .
```

---

## Prompt Reference

| Task | Prompt |
|------|--------|
| Create project | "Create a new microservice called {name}" |
| Add feature | "Add a {name} feature to my project" |
| TDD workflow | "Get the TDD workflow for {feature}" |
| Naming rules | "What are the naming conventions?" |
| Project structure | "What's the recommended project structure?" |
| Validate code | "Validate this code against architecture rules" |
| Check architecture | "Check my codebase for violations" |
| Best practices | "Show best practices for {category}" |
| List rules | "List all {category} rules" |
| Get rule details | "Explain the {rule-id} rule" |
| Custom rules | "Initialize custom architecture rules" |

---

## Tech Stack

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.115.x | Web framework |
| pydantic | 2.10.x | Validation |
| pydantic-settings | 2.7.x | Configuration |
| structlog | 24.4.x | Logging |
| uvicorn | 0.34.x | Server |
| pytest | 8.3.x | Testing |
| pytest-cov | 6.0.x | Coverage |
| pytest-asyncio | 0.25.x | Async tests |
| httpx | 0.28.x | HTTP client |
| ruff | 0.9.x | Linting |

---

## Summary

Build microservices with prompts:

```
1. "Create a new microservice called product-service"
   → Complete project scaffolded

2. "Add a product feature to my project"
   → Feature with schemas, service, router, tests

3. "Validate my code"
   → Architecture compliance check

4. "Show best practices for testing"
   → Guidance and examples
```

Everything follows:
- ✅ Consistent naming conventions
- ✅ TDD workflow (tests included)
- ✅ 80% coverage requirement
- ✅ Clean architecture
- ✅ Security rules
