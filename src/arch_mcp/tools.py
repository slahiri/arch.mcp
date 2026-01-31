"""MCP Tools for architecture validation"""

import fnmatch
import re

from .config import flatten_rules, get_rules_source, load_rules
from .structures import FILE_TEMPLATES, NAMING_CONVENTIONS, STRUCTURES


def _get_all_rules() -> list[dict]:
    """Get all rules as a flat list."""
    return flatten_rules(load_rules())


def _get_rules_by_category() -> dict[str, list[dict]]:
    """Get rules grouped by category."""
    return load_rules()


def list_rules(category: str | None = None, severity: str | None = None) -> dict:
    """List Python API architecture rules."""
    rules_by_cat = load_rules()
    all_rules = flatten_rules(rules_by_cat)

    rules = all_rules
    if category:
        rules = [r for r in rules if r.get("category") == category.lower()]
    if severity:
        rules = [r for r in rules if r.get("severity") == severity.lower()]

    return {
        "rules": [
            {
                "id": r["id"],
                "name": r["name"],
                "severity": r.get("severity", "info"),
                "category": r["category"],
                "description": r.get("description", r.get("message", "")),
            }
            for r in rules
        ],
        "total": len(rules),
        "categories": list(rules_by_cat.keys()),
        "rules_source": get_rules_source(),
    }


def get_rule(rule_id: str) -> dict:
    """Get full details of a rule including code examples."""
    all_rules = _get_all_rules()
    rule = next((r for r in all_rules if r["id"] == rule_id), None)

    if not rule:
        return {"error": f"Rule '{rule_id}' not found"}
    return {"rule": rule}


def validate_code(content: str, file_path: str) -> dict:
    """Validate Python code against architecture rules."""
    if not file_path.endswith(".py"):
        return {"valid": True, "violations": [], "message": "Not a Python file"}

    violations = []
    all_rules = _get_all_rules()

    for rule in all_rules:
        pattern = rule.get("pattern")
        if not pattern:
            continue

        applies_to = rule.get("applies_to", ["**/*.py"])
        exclude = rule.get("exclude", [])

        # Ensure lists
        if isinstance(applies_to, str):
            applies_to = [applies_to]
        if isinstance(exclude, str):
            exclude = [exclude]

        applies = any(fnmatch.fnmatch(file_path, p) for p in applies_to)
        excluded = any(fnmatch.fnmatch(file_path, p) for p in exclude)

        if not applies or excluded:
            continue

        for line_num, line in enumerate(content.split("\n"), 1):
            try:
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    violations.append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "severity": rule.get("severity", "warning"),
                        "category": rule["category"],
                        "line": line_num,
                        "column": match.start() + 1,
                        "match": match.group(0)[:50],
                        "message": rule.get("message", rule.get("description", "")),
                        "fix": rule.get("fix"),
                    })
            except re.error:
                continue

    errors = sum(1 for v in violations if v["severity"] == "error")
    warnings = sum(1 for v in violations if v["severity"] == "warning")

    return {
        "file_path": file_path,
        "valid": errors == 0,
        "violations": violations,
        "summary": {"errors": errors, "warnings": warnings},
    }


def get_project_structure(pattern: str = "clean-architecture") -> dict:
    """Get recommended Python API project structure."""
    if pattern not in STRUCTURES:
        return {"error": f"Unknown pattern '{pattern}'", "available": list(STRUCTURES.keys())}
    return {"pattern": pattern, **STRUCTURES[pattern]}


def get_best_practices(category: str) -> dict:
    """Get best practices for a category with code examples."""
    rules_by_cat = _get_rules_by_category()
    if category not in rules_by_cat:
        return {"error": f"Unknown category '{category}'", "categories": list(rules_by_cat.keys())}

    practices = [r for r in rules_by_cat[category] if r.get("best_practice") or r.get("example")]
    return {"category": category, "best_practices": practices, "total": len(practices)}


def check_architecture(files: list[dict], pattern: str = "clean-architecture") -> dict:
    """Check if a codebase follows the architecture pattern consistently."""
    issues = []
    structure = STRUCTURES.get(pattern, {})
    layers = structure.get("layers", {})

    for file in files:
        path = file.get("path", "")
        content = file.get("content", "")

        # Determine current layer
        current_layer = None
        for layer in layers:
            in_layer = (
                f"/{layer}/" in path
                or path.startswith(f"{layer}/")
                or path.startswith(f"src/{layer}/")
            )
            if in_layer:
                current_layer = layer
                break

        if current_layer:
            layer_rules = layers.get(current_layer, {})
            cannot_import = layer_rules.get("cannot_import", [])

            import_pattern = r"from\s+(\S+)\s+import|import\s+(\S+)"
            for line_num, line in enumerate(content.split("\n"), 1):
                for match in re.finditer(import_pattern, line):
                    imported = match.group(1) or match.group(2)
                    for forbidden in cannot_import:
                        if forbidden in imported:
                            msg = f"Layer '{current_layer}' cannot import from '{forbidden}'"
                            issues.append({
                                "type": "layer-violation",
                                "severity": "error",
                                "file": path,
                                "line": line_num,
                                "message": msg,
                                "import": imported,
                            })

        # Code violations
        for v in validate_code(content, path).get("violations", []):
            issues.append({
                "type": "code-violation",
                "severity": v["severity"],
                "file": path,
                "line": v["line"],
                "message": v["message"],
                "rule_id": v["rule_id"],
            })

    errors = sum(1 for i in issues if i["severity"] == "error")
    warnings = sum(1 for i in issues if i["severity"] == "warning")

    return {
        "pattern": pattern,
        "files_checked": len(files),
        "consistent": errors == 0,
        "issues": issues,
        "summary": {"errors": errors, "warnings": warnings},
    }


def get_architecture_guide() -> dict:
    """Get a complete guide for building consistent Python APIs."""
    rules_by_cat = _get_rules_by_category()
    return {
        "overview": "Architecture guide for Python APIs with FastAPI",
        "recommended_pattern": "clean-architecture",
        "layers": {
            "api": {
                "purpose": "HTTP layer - request handling, validation, routing",
                "rules": ["Use Pydantic schemas", "No business logic", "No direct DB access"],
            },
            "application": {
                "purpose": "Business logic and use cases",
                "rules": ["Orchestrate domain logic", "Define interfaces", "No HTTP concerns"],
            },
            "domain": {
                "purpose": "Core business entities and rules",
                "rules": ["NO external dependencies", "Pure Python only", "Framework agnostic"],
            },
            "infrastructure": {
                "purpose": "External concerns - database, APIs",
                "rules": ["Implement interfaces", "SQLAlchemy models here"],
            },
            "core": {
                "purpose": "Configuration and cross-cutting",
                "rules": ["Can be imported by any layer", "No business logic"],
            },
        },
        "dependency_flow": "api → application → domain ← infrastructure",
        "categories": list(rules_by_cat.keys()),
        "rules_source": get_rules_source(),
    }


def get_naming_conventions() -> dict:
    """Get mandatory naming conventions for files, classes, and functions."""
    return {
        "overview": "Mandatory naming conventions for consistent Python APIs",
        "conventions": NAMING_CONVENTIONS,
        "note": "These conventions are NOT optional. All code must follow these patterns.",
    }


def get_file_template(template_type: str, resource: str) -> dict:
    """Generate a file template for a given resource.

    Args:
        template_type: One of 'router', 'schemas', 'service', 'repository', 'errors'
        resource: The resource name in singular form (e.g., 'user', 'order')
    """
    if template_type not in FILE_TEMPLATES:
        return {
            "error": f"Unknown template type '{template_type}'",
            "available": list(FILE_TEMPLATES.keys()),
        }

    # Generate names
    resource_lower = resource.lower()
    resource_pascal = "".join(word.capitalize() for word in resource_lower.split("_"))
    resource_plural = resource_lower + "s"  # Simple pluralization

    template = FILE_TEMPLATES[template_type]
    content = template.format(
        feature=resource_lower,
        resource=resource_lower,
        resources=resource_plural,
        Resource=resource_pascal,
    )

    if template_type != "errors":
        filename = f"{resource_lower}_{template_type}.py"
    else:
        filename = "errors.py"

    return {
        "template_type": template_type,
        "resource": resource,
        "filename": filename,
        "content": content,
    }


def get_tdd_workflow(feature: str) -> dict:
    """Get the TDD workflow for implementing a new feature.

    Args:
        feature: The feature/resource name (e.g., 'user', 'order')
    """
    feature_lower = feature.lower()
    feature_pascal = "".join(word.capitalize() for word in feature_lower.split("_"))

    return {
        "overview": f"TDD workflow for implementing '{feature}' feature",
        "principle": "Write tests FIRST, then implement. Red → Green → Refactor.",
        "steps": [
            {
                "step": 1,
                "name": "Write failing test for schemas",
                "description": "Define expected request/response shapes",
                "file": f"tests/features/{feature_lower}/test_schemas.py",
                "example": f'''import pytest
from pydantic import ValidationError

def test_{feature_lower}_create_requires_name():
    """Test that {feature_pascal}Create requires a name field."""
    from src.features.{feature_lower}.schemas import {feature_pascal}Create

    with pytest.raises(ValidationError):
        {feature_pascal}Create()  # Missing required fields

def test_{feature_lower}_create_valid():
    """Test valid {feature_pascal}Create schema."""
    from src.features.{feature_lower}.schemas import {feature_pascal}Create

    data = {feature_pascal}Create(name="Test")
    assert data.name == "Test"
''',
            },
            {
                "step": 2,
                "name": "Implement schemas to pass tests",
                "description": "Create minimal Pydantic models",
                "file": f"src/features/{feature_lower}/schemas.py",
                "run": "pytest tests/features/{feature_lower}/test_schemas.py -v",
            },
            {
                "step": 3,
                "name": "Write failing test for service",
                "description": "Define expected business logic behavior",
                "file": f"tests/features/{feature_lower}/test_service.py",
                "example": f'''import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create_{feature_lower}():
    """Test {feature_pascal}Service.create returns created entity."""
    from src.features.{feature_lower}.service import {feature_pascal}Service
    from src.features.{feature_lower}.schemas import {feature_pascal}Create

    mock_repo = AsyncMock()
    mock_repo.save.return_value = {{"id": "123", "name": "Test"}}

    service = {feature_pascal}Service(repository=mock_repo)
    result = await service.create({feature_pascal}Create(name="Test"))

    assert result["id"] == "123"
    mock_repo.save.assert_called_once()

@pytest.mark.asyncio
async def test_get_{feature_lower}_not_found():
    """Test {feature_pascal}Service raises error when not found."""
    from src.features.{feature_lower}.service import {feature_pascal}Service
    from src.features.{feature_lower}.errors import {feature_pascal}NotFoundError

    mock_repo = AsyncMock()
    mock_repo.get.return_value = None

    service = {feature_pascal}Service(repository=mock_repo)

    with pytest.raises({feature_pascal}NotFoundError):
        await service.get_by_id("nonexistent")
''',
            },
            {
                "step": 4,
                "name": "Implement service to pass tests",
                "description": "Create service with business logic",
                "file": f"src/features/{feature_lower}/service.py",
                "run": "pytest tests/features/{feature_lower}/test_service.py -v",
            },
            {
                "step": 5,
                "name": "Write failing test for API endpoints",
                "description": "Define expected HTTP behavior",
                "file": f"tests/features/{feature_lower}/test_router.py",
                "example": f'''import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_create_{feature_lower}_returns_201():
    """Test POST /{feature_lower}s returns 201 with created entity."""
    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/{feature_lower}s/", json={{"name": "Test"}})

    assert response.status_code == 201
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_get_{feature_lower}_returns_404():
    """Test GET /{feature_lower}s/{{id}} returns 404 when not found."""
    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/{feature_lower}s/nonexistent")

    assert response.status_code == 404
''',
            },
            {
                "step": 6,
                "name": "Implement router to pass tests",
                "description": "Create FastAPI router with endpoints",
                "file": f"src/features/{feature_lower}/router.py",
                "run": "pytest tests/features/{feature_lower}/test_router.py -v",
            },
            {
                "step": 7,
                "name": "Run all tests and refactor",
                "description": "Ensure all tests pass, then refactor for clarity",
                "run": (
                    f"pytest tests/features/{feature_lower}/ -v "
                    f"--cov=src/features/{feature_lower}"
                ),
            },
        ],
        "test_commands": {
            "run_all": "pytest tests/ -v",
            "run_feature": f"pytest tests/features/{feature_lower}/ -v",
            "with_coverage": (
                f"pytest tests/features/{feature_lower}/ -v "
                f"--cov=src/features/{feature_lower} --cov-report=term-missing"
            ),
            "watch_mode": f"pytest-watch tests/features/{feature_lower}/",
        },
        "coverage_requirement": "Minimum 80% code coverage required",
    }


def init_rules() -> dict:
    """Initialize a custom rules file in the current directory."""
    from .config import init_custom_rules
    init_custom_rules()
    return {"status": "ok", "message": "Custom rules file created"}


def scaffold_project(name: str, description: str = "") -> dict:
    """Scaffold a new Python microservice project.

    Args:
        name: Project name (e.g., 'product-service', 'user-api')
        description: Optional project description
    """
    from pathlib import Path

    from .scaffold import scaffold_project as do_scaffold

    try:
        do_scaffold(name, Path.cwd())
        return {
            "status": "ok",
            "message": f"Project '{name}' scaffolded successfully",
            "project_path": str(Path.cwd() / name),
            "next_steps": [
                f"cd {name}",
                "python -m venv .venv",
                "source .venv/bin/activate  # Windows: .venv\\Scripts\\activate",
                "pip install -e '.[dev]'",
                "pytest  # Run tests",
                "uvicorn src.main:app --reload  # Start server",
            ],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def scaffold_feature(feature_name: str) -> dict:
    """Scaffold a new feature module with all required files.

    Creates the full feature structure following TDD:
    - schemas.py (Pydantic models)
    - errors.py (Custom exceptions)
    - repository.py (Data access interface)
    - service.py (Business logic)
    - router.py (API endpoints)
    - tests/ (Test files)

    Args:
        feature_name: Feature name in singular form (e.g., 'product', 'user', 'order')
    """
    from pathlib import Path

    feature = feature_name.lower().replace("-", "_").replace(" ", "_")
    feature_pascal = "".join(word.capitalize() for word in feature.split("_"))
    feature_plural = feature + "s"

    # Check if we're in a project directory
    src_dir = Path.cwd() / "src" / "features"
    tests_dir = Path.cwd() / "tests" / "features"

    if not src_dir.exists():
        return {
            "status": "error",
            "message": "Not in a project directory. Run scaffold_project first.",
        }

    feature_dir = src_dir / feature
    test_dir = tests_dir / feature

    if feature_dir.exists():
        return {
            "status": "error",
            "message": f"Feature '{feature}' already exists at {feature_dir}",
        }

    # Create directories
    feature_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    # schemas.py
    (feature_dir / "schemas.py").write_text(f'''"""Pydantic schemas for {feature}."""
from decimal import Decimal

from pydantic import BaseModel, Field


class {feature_pascal}Create(BaseModel):
    """Request schema for creating a {feature}."""

    name: str = Field(..., min_length=1, max_length=200)
    # Add more fields as needed


class {feature_pascal}Update(BaseModel):
    """Request schema for updating a {feature}."""

    name: str | None = Field(None, min_length=1, max_length=200)


class {feature_pascal}Response(BaseModel):
    """Response schema for {feature}."""

    id: str
    name: str

    model_config = {{"from_attributes": True}}
''')

    # errors.py
    (feature_dir / "errors.py").write_text(f'''"""Custom exceptions for {feature}."""
from src.shared.errors import AppError


class {feature_pascal}Error(AppError):
    """Base error for {feature} operations."""

    pass


class {feature_pascal}NotFoundError({feature_pascal}Error):
    """Raised when {feature} is not found."""

    def __init__(self, {feature}_id: str):
        self.{feature}_id = {feature}_id
        super().__init__(
            message=f"{feature_pascal} '{{ {feature}_id }}' not found",
            code="{feature.upper()}_NOT_FOUND",
            status_code=404,
        )


class {feature_pascal}ValidationError({feature_pascal}Error):
    """Raised when {feature} validation fails."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="{feature.upper()}_VALIDATION_ERROR",
            status_code=400,
        )
''')

    # repository.py
    (feature_dir / "repository.py").write_text(f'''"""Data access for {feature}."""
import uuid
from typing import Protocol


class {feature_pascal}Repository(Protocol):
    """Repository interface for {feature} persistence."""

    async def save(self, entity: dict) -> dict:
        """Save and return with generated id."""
        ...

    async def get(self, {feature}_id: str) -> dict | None:
        """Get by id, returns None if not found."""
        ...

    async def delete(self, {feature}_id: str) -> bool:
        """Delete, returns True if deleted."""
        ...

    async def list_all(self) -> list[dict]:
        """List all {feature_plural}."""
        ...


class InMemory{feature_pascal}Repository:
    """In-memory implementation for development/testing."""

    def __init__(self):
        self._{feature_plural}: dict[str, dict] = {{}}

    async def save(self, entity: dict) -> dict:
        {feature}_id = str(uuid.uuid4())
        record = {{"id": {feature}_id, **entity}}
        self._{feature_plural}[{feature}_id] = record
        return record

    async def get(self, {feature}_id: str) -> dict | None:
        return self._{feature_plural}.get({feature}_id)

    async def delete(self, {feature}_id: str) -> bool:
        if {feature}_id in self._{feature_plural}:
            del self._{feature_plural}[{feature}_id]
            return True
        return False

    async def list_all(self) -> list[dict]:
        return list(self._{feature_plural}.values())
''')

    # service.py
    (feature_dir / "service.py").write_text(f'''"""Business logic for {feature}."""
import structlog

from .errors import {feature_pascal}NotFoundError
from .repository import {feature_pascal}Repository
from .schemas import {feature_pascal}Create

logger = structlog.get_logger()


class {feature_pascal}Service:
    """Service for {feature} operations."""

    def __init__(self, repository: {feature_pascal}Repository):
        self._repository = repository

    async def create(self, data: {feature_pascal}Create) -> dict:
        """Create a new {feature}."""
        logger.info("creating_{feature}", name=data.name)

        entity = data.model_dump()
        result = await self._repository.save(entity)

        logger.info("{feature}_created", {feature}_id=result["id"])
        return result

    async def get_by_id(self, {feature}_id: str) -> dict:
        """Get a {feature} by id."""
        result = await self._repository.get({feature}_id)

        if not result:
            logger.warning("{feature}_not_found", {feature}_id={feature}_id)
            raise {feature_pascal}NotFoundError({feature}_id)

        return result

    async def list_all(self) -> list[dict]:
        """List all {feature_plural}."""
        return await self._repository.list_all()
''')

    # router.py
    (feature_dir / "router.py").write_text(f'''"""API routes for {feature}."""
from fastapi import APIRouter, Depends, HTTPException, status

from .errors import {feature_pascal}NotFoundError
from .repository import InMemory{feature_pascal}Repository, {feature_pascal}Repository
from .schemas import {feature_pascal}Create, {feature_pascal}Response
from .service import {feature_pascal}Service

router = APIRouter(prefix="/api/{feature_plural}", tags=["{feature_plural}"])

# Dependency injection
_repository = InMemory{feature_pascal}Repository()


def get_repository() -> {feature_pascal}Repository:
    return _repository


def get_{feature}_service(
    repository: {feature_pascal}Repository = Depends(get_repository),
) -> {feature_pascal}Service:
    return {feature_pascal}Service(repository=repository)


@router.post("/", response_model={feature_pascal}Response, status_code=status.HTTP_201_CREATED)
async def create_{feature}(
    data: {feature_pascal}Create,
    service: {feature_pascal}Service = Depends(get_{feature}_service),
) -> {feature_pascal}Response:
    """Create a new {feature}."""
    result = await service.create(data)
    return {feature_pascal}Response(**result)


@router.get("/{{{feature}_id}}", response_model={feature_pascal}Response)
async def get_{feature}(
    {feature}_id: str,
    service: {feature_pascal}Service = Depends(get_{feature}_service),
) -> {feature_pascal}Response:
    """Get a {feature} by id."""
    try:
        result = await service.get_by_id({feature}_id)
        return {feature_pascal}Response(**result)
    except {feature_pascal}NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)


@router.get("/", response_model=list[{feature_pascal}Response])
async def list_{feature_plural}(
    service: {feature_pascal}Service = Depends(get_{feature}_service),
) -> list[{feature_pascal}Response]:
    """List all {feature_plural}."""
    results = await service.list_all()
    return [{feature_pascal}Response(**r) for r in results]
''')

    # __init__.py
    (feature_dir / "__init__.py").write_text(f'''"""{feature_pascal} feature module."""
from .router import router

__all__ = ["router"]
''')

    # Test files
    (test_dir / "__init__.py").write_text("")

    (test_dir / "test_schemas.py").write_text(f'''"""Tests for {feature} schemas."""
import pytest
from pydantic import ValidationError


class Test{feature_pascal}Create:
    def test_valid_{feature}(self):
        from src.features.{feature}.schemas import {feature_pascal}Create

        data = {feature_pascal}Create(name="Test")
        assert data.name == "Test"

    def test_name_required(self):
        from src.features.{feature}.schemas import {feature_pascal}Create

        with pytest.raises(ValidationError):
            {feature_pascal}Create()
''')

    (test_dir / "test_service.py").write_text(f'''"""Tests for {feature} service."""
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.save.return_value = {{"id": "123", "name": "Test"}}
    repo.get.return_value = None
    return repo


class Test{feature_pascal}ServiceCreate:
    @pytest.mark.asyncio
    async def test_create_returns_{feature}(self, mock_repository):
        from src.features.{feature}.service import {feature_pascal}Service
        from src.features.{feature}.schemas import {feature_pascal}Create

        service = {feature_pascal}Service(repository=mock_repository)
        result = await service.create({feature_pascal}Create(name="Test"))

        assert result["id"] == "123"
        mock_repository.save.assert_called_once()


class Test{feature_pascal}ServiceGetById:
    @pytest.mark.asyncio
    async def test_raises_not_found(self, mock_repository):
        from src.features.{feature}.service import {feature_pascal}Service
        from src.features.{feature}.errors import {feature_pascal}NotFoundError

        service = {feature_pascal}Service(repository=mock_repository)

        with pytest.raises({feature_pascal}NotFoundError):
            await service.get_by_id("nonexistent")
''')

    (test_dir / "test_router.py").write_text(f'''"""Tests for {feature} API endpoints."""
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    from src.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


class TestCreate{feature_pascal}:
    @pytest.mark.asyncio
    async def test_returns_201(self, client):
        response = await client.post("/api/{feature_plural}/", json={{"name": "Test"}})
        assert response.status_code == 201


class TestGet{feature_pascal}:
    @pytest.mark.asyncio
    async def test_not_found_returns_404(self, client):
        response = await client.get("/api/{feature_plural}/nonexistent")
        assert response.status_code == 404
''')

    return {
        "status": "ok",
        "message": f"Feature '{feature}' scaffolded successfully",
        "files_created": [
            f"src/features/{feature}/schemas.py",
            f"src/features/{feature}/errors.py",
            f"src/features/{feature}/repository.py",
            f"src/features/{feature}/service.py",
            f"src/features/{feature}/router.py",
            f"src/features/{feature}/__init__.py",
            f"tests/features/{feature}/test_schemas.py",
            f"tests/features/{feature}/test_service.py",
            f"tests/features/{feature}/test_router.py",
        ],
        "next_steps": [
            f"Add 'from src.features.{feature} import router as {feature}_router' to src/main.py",
            f"Add 'app.include_router({feature}_router)' to src/main.py",
            "Run: pytest tests/features/{feature}/ -v",
            "Customize schemas, service logic as needed",
        ],
    }
