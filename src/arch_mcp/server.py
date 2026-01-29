"""
Architecture Controls MCP Server

An MCP server providing architecture rules and best practices for Python APIs.
Built with FastMCP 3.0.
"""

from fastmcp import FastMCP

from .rules import RULES
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
    return json.dumps({"categories": list(RULES.keys())}, indent=2)


@mcp.resource("arch://guide")
def resource_guide() -> str:
    """Architecture guide"""
    import json
    return json.dumps(get_architecture_guide(), indent=2)


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
