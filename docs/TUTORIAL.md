# Tutorial: Build a Microservice with Claude Prompts

Build a complete Python microservice using only Claude prompts.

## Prerequisites

- Claude Code with arch-mcp connected
- Python 3.11+

```bash
claude mcp add --transport sse arch-controls https://arch-mcp.sid.sh/sse
```

---

## Step 1: Create the Project

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

---

## Step 2: Test the Setup

```bash
cd product-service
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -v
```

Expected output:
```
tests/test_health.py::test_health_returns_ok PASSED
tests/test_health.py::test_readiness_returns_ready PASSED

======================== 2 passed ========================
```

---

## Step 3: Run the Server

```bash
uvicorn src.main:app --reload
```

Test the health endpoint:
```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/api/health/ready
# {"status":"ready"}
```

---

## Step 4: Add an API

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

---

## Step 5: Test the API

### Run Tests

```bash
pytest tests/features/product/ -v
```

Expected output:
```
test_schemas.py::TestProductCreate::test_valid_product PASSED
test_schemas.py::TestProductCreate::test_name_required PASSED
test_service.py::TestProductServiceCreate::test_create_returns_product PASSED
test_service.py::TestProductServiceGetById::test_raises_not_found PASSED
test_router.py::TestCreateProduct::test_returns_201 PASSED
test_router.py::TestGetProduct::test_not_found_returns_404 PASSED

======================== 6 passed ========================
```

### Test Manually

```bash
# Start server
uvicorn src.main:app --reload

# Create a product
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Widget"}'

# Response: {"id":"abc-123","name":"Widget"}

# Get product
curl http://localhost:8000/api/products/abc-123

# List products
curl http://localhost:8000/api/products/

# Not found
curl http://localhost:8000/api/products/invalid
# {"detail":"Product 'invalid' not found"}
```

---

## Step 6: Customize the Schema

Add fields to `src/features/product/schemas.py`:

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

Update tests and run again:
```bash
pytest tests/features/product/ -v
```

---

## Step 7: Validate Architecture

> **"Check my codebase for architecture violations"**

Output:
```
✓ No architecture violations found

Checked:
  - Layer dependencies
  - Naming conventions
  - Security patterns
```

---

## Step 8: Run Full Test Suite

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

Expected:
```
======================== 8 passed ========================
TOTAL    xxx    xx    85%
```

---

## Summary

| Step | Command/Prompt | Result |
|------|----------------|--------|
| 1 | "Create a new microservice called product-service" | Project scaffolded |
| 2 | `pytest -v` | 2 tests pass |
| 3 | `uvicorn src.main:app --reload` | Server running |
| 4 | "Add a product feature to my project" | API scaffolded |
| 5 | `pytest tests/features/product/ -v` | 6 tests pass |
| 6 | Edit schemas | Customize fields |
| 7 | "Check my codebase for violations" | Architecture valid |
| 8 | `pytest --cov=src --cov-fail-under=80` | 80%+ coverage |

---

## Next Steps

**Add more features:**
> "Add an order feature to my project"

**Get guidance:**
> "What are the naming conventions?"
> "Show best practices for error-handling"

**Production:**
> "How should I containerize this service?"

---

## Prompt Reference

| Task | Prompt |
|------|--------|
| Create project | "Create a new microservice called {name}" |
| Add feature | "Add a {name} feature to my project" |
| TDD workflow | "Get the TDD workflow for {feature}" |
| Naming rules | "What are the naming conventions?" |
| Validate code | "Validate this code against architecture rules" |
| Check architecture | "Check my codebase for violations" |
| Best practices | "Show best practices for {category}" |
| List rules | "List all {category} rules" |

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
