"""
Architecture Controls MCP Server

An MCP server providing architecture rules and best practices for Python APIs.
Built with FastMCP 3.0.
"""

import os

from fastmcp import FastMCP

from .tools import (
    check_architecture,
    get_architecture_guide,
    get_best_practices,
    get_project_structure,
    get_rule,
    list_rules,
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
        category: Filter by category (security, data-access, error-handling,
            api-design, logging, configuration, testing)
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
        category: Category (security, data-access, error-handling, api-design,
            logging, configuration, testing)
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


def init_database():
    """Initialize database and seed data if needed."""
    if not os.environ.get("DATABASE_URL"):
        return

    from .db import fetch_rules, init_db, seed_rules, seed_structures
    from .rules import ALL_RULES
    from .structures import STRUCTURES

    # Initialize tables
    init_db()

    # Seed if empty
    existing = fetch_rules()
    if not existing:
        seed_rules(ALL_RULES)
        seed_structures(STRUCTURES)
        print("Database seeded with default rules and structures")


def main():
    """Run the MCP server.

    Supports two modes:
    - stdio (default): For local CLI usage with Claude Code/Cursor
    - http: For hosted service deployment (set MCP_TRANSPORT=http)

    Environment variables:
    - MCP_TRANSPORT: "stdio" (default) or "http"
    - MCP_HOST: Host to bind (default: "0.0.0.0")
    - MCP_PORT: Port to bind (default: 8000)
    - DATABASE_URL: PostgreSQL connection string (optional)
    - REDIS_URL: Redis connection string (optional)
    """
    # Initialize database if configured
    init_database()

    transport = os.environ.get("MCP_TRANSPORT", "stdio")

    if transport == "http":
        host = os.environ.get("MCP_HOST", "0.0.0.0")
        # Railway sets PORT, fallback to MCP_PORT or 8000
        port = int(os.environ.get("PORT", os.environ.get("MCP_PORT", "8000")))
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
