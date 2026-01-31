"""
Architecture Controls MCP Server

An MCP server providing architecture rules and best practices for Python APIs.
Built with FastMCP.
"""

import os

from fastmcp import FastMCP

from .tools import (
    check_architecture,
    get_architecture_guide,
    get_best_practices,
    get_file_template,
    get_naming_conventions,
    get_project_structure,
    get_rule,
    get_tdd_workflow,
    init_rules,
    list_rules,
    scaffold_feature,
    scaffold_project,
    validate_code,
)

# Create MCP server
mcp = FastMCP("arch-controls")


# ============================================================================
# TOOLS
# ============================================================================


@mcp.tool()
def tool_list_rules(category: str | None = None, severity: str | None = None) -> dict:
    """
    List Python API architecture rules.

    Args:
        category: Filter by category (naming, structure, security, data-access,
            error-handling, api-design, logging, configuration, testing)
        severity: Filter by severity (error, warning, info)
    """
    return list_rules(category, severity)


@mcp.tool()
def tool_get_rule(rule_id: str) -> dict:
    """
    Get full details of a rule including code examples.

    Args:
        rule_id: Rule identifier (e.g., "use-repository-pattern", "no-bare-except")
    """
    return get_rule(rule_id)


@mcp.tool()
def tool_validate_code(content: str, file_path: str) -> dict:
    """
    Validate Python code against architecture rules.

    Args:
        content: Python file content to validate
        file_path: File path for context (e.g., "src/api/routes/users.py")
    """
    return validate_code(content, file_path)


@mcp.tool()
def tool_get_project_structure(pattern: str = "clean-architecture") -> dict:
    """
    Get recommended Python API project structure.

    Args:
        pattern: Architecture pattern ("clean-architecture", "feature-based", or "simple")
    """
    return get_project_structure(pattern)


@mcp.tool()
def tool_get_best_practices(category: str) -> dict:
    """
    Get best practices for a category with code examples.

    Args:
        category: Category (naming, structure, security, data-access, error-handling,
            api-design, logging, configuration, testing)
    """
    return get_best_practices(category)


@mcp.tool()
def tool_check_architecture(files: list[dict], pattern: str = "clean-architecture") -> dict:
    """
    Check if a codebase follows the architecture pattern consistently.

    Args:
        files: List of files with {"path": "...", "content": "..."}
        pattern: Architecture pattern ("clean-architecture", "feature-based", "simple")
    """
    return check_architecture(files, pattern)


@mcp.tool()
def tool_get_architecture_guide() -> dict:
    """
    Get a complete guide for building consistent Python APIs.

    Returns the recommended patterns, rules, and examples for each layer.
    """
    return get_architecture_guide()


@mcp.tool()
def tool_get_naming_conventions() -> dict:
    """
    Get mandatory naming conventions for files, classes, and functions.

    Returns the required naming patterns that ALL code must follow.
    These are NOT optional - they ensure consistency across all projects.
    """
    return get_naming_conventions()


@mcp.tool()
def tool_get_file_template(template_type: str, resource: str) -> dict:
    """
    Generate a file template for a given resource.

    Args:
        template_type: One of "router", "schemas", "service", "repository", "errors"
        resource: The resource name in singular form (e.g., "user", "order", "product")

    Returns a ready-to-use file with correct naming conventions applied.
    """
    return get_file_template(template_type, resource)


@mcp.tool()
def tool_get_tdd_workflow(feature: str) -> dict:
    """
    Get the TDD workflow for implementing a new feature.

    Returns step-by-step instructions for Test-Driven Development:
    1. Write failing tests first
    2. Implement minimal code to pass
    3. Refactor while keeping tests green

    Args:
        feature: The feature/resource name (e.g., "user", "order", "payment")

    TDD is MANDATORY - all features must be developed test-first.
    """
    return get_tdd_workflow(feature)


@mcp.tool()
def tool_init_rules() -> dict:
    """
    Initialize a custom rules file in the current directory.

    Creates .arch-mcp/rules.yaml with default rules that you can customize.
    Edit this file to add, remove, or modify architecture rules for your project.
    """
    return init_rules()


@mcp.tool()
def tool_scaffold_project(name: str, description: str = "") -> dict:
    """
    Scaffold a new Python microservice project.

    Creates a complete project structure with:
    - FastAPI setup with health endpoints
    - Pydantic settings configuration
    - Structured logging with structlog
    - Pytest setup with 80% coverage requirement
    - Docker and docker-compose files
    - GitHub Actions CI/CD workflow
    - Base error classes and shared schemas

    Args:
        name: Project name (e.g., 'product-service', 'user-api')
        description: Optional project description

    Example: "Scaffold a new project called order-service"
    """
    return scaffold_project(name, description)


@mcp.tool()
def tool_scaffold_feature(feature_name: str) -> dict:
    """
    Scaffold a new feature module with all required files.

    Creates the complete feature structure following TDD and naming conventions:
    - schemas.py (Pydantic request/response models)
    - errors.py (Custom exception classes)
    - repository.py (Data access interface + in-memory implementation)
    - service.py (Business logic)
    - router.py (FastAPI endpoints with dependency injection)
    - Test files for schemas, service, and router

    Args:
        feature_name: Feature name in singular form (e.g., 'product', 'user', 'order')

    Example: "Add a product feature to my project"

    Note: Must be run from within a scaffolded project directory.
    """
    return scaffold_feature(feature_name)


# ============================================================================
# RESOURCES
# ============================================================================


@mcp.resource("arch://rules")
def resource_rules() -> str:
    """All Python API architecture rules"""
    import json
    return json.dumps(list_rules(), indent=2)


@mcp.resource("arch://categories")
def resource_categories() -> str:
    """All rule categories"""
    import json
    result = list_rules()
    return json.dumps({"categories": result.get("categories", [])}, indent=2)


@mcp.resource("arch://guide")
def resource_guide() -> str:
    """Architecture guide"""
    import json
    return json.dumps(get_architecture_guide(), indent=2)


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Run the MCP server.

    Supports two modes:
    - stdio (default): For local CLI usage with Claude Code/Cursor
    - http/sse: For hosted service deployment (set MCP_TRANSPORT=http)

    Environment variables:
    - MCP_TRANSPORT: "stdio" (default) or "http"
    - PORT: Port to bind for HTTP mode (default: 8000)
    """
    transport = os.environ.get("MCP_TRANSPORT", "stdio")

    if transport == "http":
        host = "0.0.0.0"
        port = int(os.environ.get("PORT", "8000"))
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
