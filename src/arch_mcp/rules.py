"""Architecture rules and best practices for Python APIs"""

RULES = {
    "naming": [
        {
            "id": "schema-naming",
            "name": "Schema naming convention",
            "severity": "error",
            "description": "Pydantic schemas must follow {Resource}Create, {Resource}Update, {Resource}Response pattern.",
            "best_practice": True,
            "example": """
# Good
class UserCreate(BaseModel): ...
class UserUpdate(BaseModel): ...
class UserResponse(BaseModel): ...
class OrderCreate(BaseModel): ...

# Bad
class CreateUser(BaseModel): ...      # Wrong order
class UserDTO(BaseModel): ...         # Don't use DTO suffix
class UserSchema(BaseModel): ...      # Don't use Schema suffix
class UserModel(BaseModel): ...       # Model is for SQLAlchemy""",
        },
        {
            "id": "service-naming",
            "name": "Service class naming",
            "severity": "error",
            "description": "Service classes must be named {Resource}Service.",
            "pattern": r"class\s+\w+(?<!Service)\s*\(.*\):\s*$",
            "applies_to": ["**/service.py", "**/*_service.py", "**/services/**"],
            "best_practice": True,
            "example": """
# Good
class UserService: ...
class OrderService: ...
class PaymentService: ...

# Bad
class UserManager: ...        # Use Service, not Manager
class UserHandler: ...        # Use Service, not Handler
class Users: ...              # Must end with Service""",
        },
        {
            "id": "repository-naming",
            "name": "Repository class naming",
            "severity": "error",
            "description": "Repository classes must be named {Resource}Repository.",
            "best_practice": True,
            "example": """
# Good
class UserRepository(Protocol): ...
class SQLAlchemyUserRepository(UserRepository): ...
class InMemoryUserRepository(UserRepository): ...

# Bad
class UserDAO: ...            # Use Repository, not DAO
class UserStore: ...          # Use Repository, not Store
class Users: ...              # Must end with Repository""",
        },
        {
            "id": "error-naming",
            "name": "Exception class naming",
            "severity": "warning",
            "description": "Custom exceptions must end with Error and describe the failure.",
            "pattern": r"class\s+\w+Exception\s*\(",
            "message": "Use 'Error' suffix instead of 'Exception' (e.g., NotFoundError).",
            "best_practice": True,
            "example": """
# Good
class UserNotFoundError(Exception): ...
class ValidationError(Exception): ...
class AuthenticationError(Exception): ...

# Bad
class UserNotFoundException(Exception): ...  # Use Error, not Exception
class UserNotFound(Exception): ...           # Must end with Error""",
        },
        {
            "id": "file-naming",
            "name": "File naming convention",
            "severity": "error",
            "description": "Files must use snake_case and follow standard suffixes.",
            "best_practice": True,
            "example": """
# Standard file names by type:
router.py or user_router.py     # API routes
schemas.py or user_schemas.py   # Pydantic models
service.py or user_service.py   # Business logic
repository.py or user_repository.py  # Data access
models.py or user_models.py     # SQLAlchemy models
errors.py                       # Custom exceptions
config.py                       # Configuration (in core/)

# Test files:
test_user_service.py            # Tests for user_service.py
conftest.py                     # Pytest fixtures""",
        },
        {
            "id": "endpoint-naming",
            "name": "API endpoint function naming",
            "severity": "warning",
            "description": "Router endpoint functions must follow CRUD naming: create_, get_, list_, update_, delete_.",
            "best_practice": True,
            "example": """
# Good
@router.post("/")
async def create_user(...): ...

@router.get("/{id}")
async def get_user(...): ...

@router.get("/")
async def list_users(...): ...

@router.put("/{id}")
async def update_user(...): ...

@router.delete("/{id}")
async def delete_user(...): ...

# Bad
@router.post("/")
async def add_user(...): ...      # Use create_, not add_

@router.get("/{id}")
async def fetch_user(...): ...    # Use get_, not fetch_""",
        },
    ],
    "structure": [
        {
            "id": "one-router-per-feature",
            "name": "One router per feature",
            "severity": "error",
            "description": "Each feature/resource should have exactly one router file.",
            "best_practice": True,
            "example": """
# Good structure:
src/features/users/router.py      # All user endpoints
src/features/orders/router.py     # All order endpoints

# Bad:
src/routes.py                     # Don't put all routes in one file
src/features/users/routes_v1.py   # Don't version at file level
src/features/users/admin_routes.py  # Don't split by role""",
        },
        {
            "id": "service-per-feature",
            "name": "One service per feature",
            "severity": "warning",
            "description": "Each feature should have one primary service class.",
            "best_practice": True,
            "example": """
# Good:
src/features/users/service.py     # Contains UserService

# Bad:
src/features/users/user_crud.py   # Wrong naming
src/features/users/user_service.py
src/features/users/admin_service.py  # Split into one service""",
        },
        {
            "id": "shared-code-location",
            "name": "Shared code in shared/",
            "severity": "error",
            "description": "Code used by multiple features must live in shared/ directory.",
            "best_practice": True,
            "example": """
# Good - shared utilities:
src/shared/pagination.py          # Pagination schemas
src/shared/errors.py              # Base error classes
src/shared/database.py            # DB session management

# Bad - duplicating across features:
src/features/users/pagination.py
src/features/orders/pagination.py  # Duplicate!""",
        },
        {
            "id": "config-location",
            "name": "Configuration in core/config.py",
            "severity": "error",
            "description": "All configuration must be in core/config.py using pydantic-settings.",
            "best_practice": True,
            "example": """
# Good:
src/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    debug: bool = False

    model_config = {"env_file": ".env"}

settings = Settings()

# Bad:
src/features/users/config.py      # No per-feature config
src/settings.py                   # Must be in core/""",
        },
        {
            "id": "test-file-location",
            "name": "Tests mirror source structure",
            "severity": "warning",
            "description": "Test files should mirror the source structure.",
            "best_practice": True,
            "example": """
# Source:
src/features/users/service.py
src/features/users/router.py

# Tests (option 1 - separate tests folder):
tests/features/users/test_service.py
tests/features/users/test_router.py

# Tests (option 2 - alongside source):
src/features/users/test_service.py
src/features/users/test_router.py""",
        },
    ],
    "security": [
        {
            "id": "no-hardcoded-secrets",
            "name": "No hardcoded secrets",
            "severity": "error",
            "description": "Never hardcode passwords, API keys, or tokens in source code.",
            "pattern": r"(password|secret|api_key|apikey|token|jwt)\s*=\s*['\"][^'\"]{8,}['\"]",
            "message": "Hardcoded secret detected. Use environment variables.",
            "fix": "Move to environment variable and access via pydantic-settings.",
        },
        {
            "id": "no-sql-string-concat",
            "name": "No SQL string concatenation",
            "severity": "error",
            "description": "Prevent SQL injection by using parameterized queries.",
            "pattern": r"(execute|raw)\s*\(\s*f['\"]|\.format\s*\([^)]*\)\s*\)|%\s*\(",
            "message": "Possible SQL injection. Use parameterized queries or ORM.",
            "fix": "Use SQLAlchemy ORM or parameterized queries.",
        },
        {
            "id": "validate-input",
            "name": "Validate all inputs",
            "severity": "error",
            "description": "Always validate request data at API boundaries using Pydantic.",
            "best_practice": True,
            "example": """
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    role: Literal['user', 'admin'] = 'user'

@router.post('/users')
async def create_user(request: CreateUserRequest):
    # request is already validated by Pydantic
    ...""",
        },
    ],
    "data-access": [
        {
            "id": "use-repository-pattern",
            "name": "Use repository pattern",
            "severity": "warning",
            "description": "Abstract database access behind repository classes for testability.",
            "best_practice": True,
            "example": """
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, id: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User) -> None: ...

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, id: str) -> User | None:
        return await self.session.get(User, id)""",
        },
        {
            "id": "no-db-in-routes",
            "name": "No database calls in route handlers",
            "severity": "warning",
            "description": "Route handlers should call services, not database directly.",
            "pattern": r"(session|db)\.(query|execute|add|delete|get|scalar)",
            "applies_to": ["**/api/**", "**/routes/**", "**/routers/**"],
            "message": "Database access should be in repositories/services, not routes.",
        },
        {
            "id": "use-async-db",
            "name": "Use async database operations",
            "severity": "info",
            "description": "Use async SQLAlchemy for non-blocking database access.",
            "best_practice": True,
            "example": """
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session""",
        },
    ],
    "error-handling": [
        {
            "id": "no-bare-except",
            "name": "No bare except",
            "severity": "error",
            "description": "Always catch specific exceptions, not bare except.",
            "pattern": r"except\s*:",
            "message": "Don't use bare 'except:'. Catch specific exceptions.",
        },
        {
            "id": "no-generic-exception",
            "name": "No generic Exception catch",
            "severity": "warning",
            "description": "Avoid catching generic Exception unless re-raising.",
            "pattern": r"except\s+Exception\s*:",
            "message": "Avoid catching generic Exception. Catch specific errors.",
        },
        {
            "id": "use-custom-exceptions",
            "name": "Use custom exceptions",
            "severity": "info",
            "description": "Define custom exception classes for different error scenarios.",
            "best_practice": True,
            "example": """
class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} '{id}' not found", "NOT_FOUND", 404)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.code})""",
        },
    ],
    "api-design": [
        {
            "id": "use-pydantic-schemas",
            "name": "Use Pydantic for request/response",
            "severity": "error",
            "description": "Always use Pydantic models for request and response schemas.",
            "best_practice": True,
            "example": """
from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    email: str
    name: str = Field(min_length=1, max_length=100)

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    model_config = {"from_attributes": True}

@router.post('/users', response_model=UserResponse)
async def create_user(request: CreateUserRequest) -> UserResponse:
    ...""",
        },
        {
            "id": "use-dependency-injection",
            "name": "Use dependency injection",
            "severity": "warning",
            "description": "Use FastAPI's Depends for dependency injection.",
            "best_practice": True,
            "example": """
from fastapi import Depends

def get_user_service(repo: UserRepository = Depends(get_repo)) -> UserService:
    return UserService(repo)

@router.get('/users/{id}')
async def get_user(id: str, service: UserService = Depends(get_user_service)):
    return await service.get_by_id(id)""",
        },
    ],
    "logging": [
        {
            "id": "no-print",
            "name": "No print statements",
            "severity": "warning",
            "pattern": r"\bprint\s*\(",
            "applies_to": ["**/*.py"],
            "exclude": ["**/tests/**", "**/*_test.py"],
            "message": "Use logging module instead of print().",
        },
        {
            "id": "use-structlog",
            "name": "Use structured logging",
            "severity": "info",
            "description": "Use structlog for structured, contextual logging.",
            "best_practice": True,
            "example": """
import structlog
logger = structlog.get_logger()

logger.info("user_created", user_id=user.id, email=user.email)
logger.error("payment_failed", user_id=user.id, error=str(e))""",
        },
    ],
    "configuration": [
        {
            "id": "no-direct-env",
            "name": "No direct env access",
            "severity": "warning",
            "pattern": r"os\.(environ|getenv)\s*[\[\(]",
            "applies_to": ["**/*.py"],
            "exclude": ["**/config.py", "**/settings.py"],
            "message": "Use pydantic-settings for configuration.",
        },
        {
            "id": "use-pydantic-settings",
            "name": "Use pydantic-settings",
            "severity": "info",
            "description": "Centralize configuration with type-safe pydantic-settings.",
            "best_practice": True,
            "example": """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    debug: bool = False

    model_config = {"env_file": ".env"}

settings = Settings()""",
        },
    ],
    "testing": [
        {
            "id": "tdd-required",
            "name": "TDD approach required",
            "severity": "error",
            "description": "All features MUST be developed using Test-Driven Development. Write tests FIRST.",
            "best_practice": True,
            "example": """
# TDD Workflow: Red → Green → Refactor

# Step 1: Write a FAILING test first
def test_user_service_creates_user():
    service = UserService(mock_repo)
    result = await service.create(UserCreate(name="Test"))
    assert result.id is not None  # This will FAIL - service doesn't exist yet

# Step 2: Write MINIMAL code to pass the test
class UserService:
    async def create(self, data: UserCreate) -> User:
        return await self._repository.save(data)  # Now test passes

# Step 3: Refactor while keeping tests green
# Add logging, validation, etc. - tests ensure nothing breaks""",
        },
        {
            "id": "test-before-implementation",
            "name": "Tests before implementation",
            "severity": "error",
            "description": "Never write implementation code without a failing test first.",
            "best_practice": True,
            "example": """
# WRONG: Writing implementation first
class UserService:
    async def create(self, data): ...  # No test exists!

# RIGHT: Write test first, then implement
# 1. test_user_service.py - write test (it fails)
# 2. user_service.py - implement (test passes)
# 3. Commit both together""",
        },
        {
            "id": "test-with-pytest",
            "name": "Use pytest for testing",
            "severity": "error",
            "description": "Use pytest with async support for API testing. No unittest.",
            "best_practice": True,
            "example": """
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_create_user():
    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/users/", json={"name": "Test"})

    assert response.status_code == 201
    assert "id" in response.json()""",
        },
        {
            "id": "test-file-naming",
            "name": "Test file naming convention",
            "severity": "error",
            "description": "Test files must be named test_{module}.py and mirror source structure.",
            "best_practice": True,
            "example": """
# Source structure:
src/features/users/service.py
src/features/users/router.py
src/features/users/schemas.py

# Test structure (must mirror):
tests/features/users/test_service.py
tests/features/users/test_router.py
tests/features/users/test_schemas.py

# Each test file tests ONE module only""",
        },
        {
            "id": "test-coverage-minimum",
            "name": "Minimum 80% test coverage",
            "severity": "error",
            "description": "All code must have at least 80% test coverage.",
            "best_practice": True,
            "example": """
# Run tests with coverage:
pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=80

# Coverage report shows untested lines:
# src/features/users/service.py    95%   Missing: 45-47
# src/features/users/router.py     88%   Missing: 23

# Add tests for missing lines before committing""",
        },
        {
            "id": "mock-external-dependencies",
            "name": "Mock external dependencies",
            "severity": "warning",
            "description": "Unit tests must mock databases, APIs, and other external services.",
            "best_practice": True,
            "example": """
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_user_repository():
    repo = AsyncMock()
    repo.save.return_value = {"id": "123", "name": "Test"}
    repo.get.return_value = {"id": "123", "name": "Test"}
    return repo

@pytest.mark.asyncio
async def test_user_service_create(mock_user_repository):
    service = UserService(repository=mock_user_repository)
    result = await service.create(UserCreate(name="Test"))

    assert result["id"] == "123"
    mock_user_repository.save.assert_called_once()""",
        },
        {
            "id": "test-isolation",
            "name": "Tests must be isolated",
            "severity": "error",
            "description": "Each test must be independent. No shared state between tests.",
            "best_practice": True,
            "example": """
# WRONG: Tests share state
class TestUserService:
    user_id = None  # Shared state!

    def test_create(self):
        self.user_id = create_user()  # Sets shared state

    def test_get(self):
        get_user(self.user_id)  # Depends on test_create running first!

# RIGHT: Each test is independent
@pytest.fixture
def user_id():
    return create_user()

def test_create():
    result = create_user()
    assert result is not None

def test_get(user_id):  # Uses fixture, not shared state
    result = get_user(user_id)
    assert result is not None""",
        },
        {
            "id": "test-happy-and-error-paths",
            "name": "Test both happy and error paths",
            "severity": "warning",
            "description": "Every function needs tests for success AND failure cases.",
            "best_practice": True,
            "example": """
# Test happy path
@pytest.mark.asyncio
async def test_get_user_success(mock_repo):
    mock_repo.get.return_value = {"id": "123", "name": "Test"}
    service = UserService(mock_repo)

    result = await service.get_by_id("123")
    assert result["name"] == "Test"

# Test error path
@pytest.mark.asyncio
async def test_get_user_not_found(mock_repo):
    mock_repo.get.return_value = None
    service = UserService(mock_repo)

    with pytest.raises(UserNotFoundError):
        await service.get_by_id("nonexistent")""",
        },
    ],
}

# Flatten rules for easy access
ALL_RULES: list[dict] = []
for category, category_rules in RULES.items():
    for rule in category_rules:
        rule["category"] = category
        ALL_RULES.append(rule)
