"""Architecture rules and best practices for Python APIs"""

RULES = {
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
            "id": "test-with-pytest",
            "name": "Use pytest for testing",
            "severity": "info",
            "description": "Use pytest with async support for API testing.",
            "best_practice": True,
            "example": """
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/api/v1/users", json={"email": "test@example.com"})
    assert response.status_code == 201""",
        },
    ],
}

# Flatten rules for easy access
ALL_RULES: list[dict] = []
for category, category_rules in RULES.items():
    for rule in category_rules:
        rule["category"] = category
        ALL_RULES.append(rule)
