# arch-mcp

[![CI](https://github.com/slahiri/arch.mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/slahiri/arch.mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/arch-mcp.svg)](https://pypi.org/project/arch-mcp/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server for Python API architecture controls. Validates code against architecture rules and best practices.

**[Tutorial: Build a Python Microservice](docs/TUTORIAL.md)** - Step-by-step guide using arch-mcp in Cursor and Claude Code.

## Remote Service

Use the hosted MCP server at `https://arch-mcp.sid.sh/sse` - no installation required.

### Claude Code

```bash
claude mcp add arch-controls --url https://arch-mcp.sid.sh/sse
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

## Running Locally

Run the MCP server on your own machine.

### Claude Code

```bash
# Via uvx (recommended)
claude mcp add arch-controls -- uvx arch-mcp

# Or via pip
pip install arch-mcp
claude mcp add arch-controls -- arch-mcp
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "arch-controls": {
      "command": "uvx",
      "args": ["arch-mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `tool_list_rules` | List architecture rules (filter by category/severity) |
| `tool_get_rule` | Get rule details with code examples |
| `tool_validate_code` | Validate code against architecture rules |
| `tool_get_project_structure` | Get recommended folder structure |
| `tool_get_best_practices` | Get best practices by category |
| `tool_check_architecture` | Check codebase for layer violations |
| `tool_get_architecture_guide` | Complete architecture guide |
| `tool_get_naming_conventions` | **Mandatory** naming patterns for files, classes, functions |
| `tool_get_file_template` | Generate starter files with correct naming |
| `tool_get_tdd_workflow` | Step-by-step TDD workflow for a feature |

## Rule Categories

- **naming** - File, class, and function naming conventions (mandatory)
- **structure** - Project organization and modularization rules
- **security** - Secrets management, SQL injection prevention, input validation
- **data-access** - Repository pattern, async database operations
- **error-handling** - Custom exceptions, specific exception catches
- **api-design** - Pydantic schemas, dependency injection
- **logging** - Structured logging, no print statements
- **configuration** - Pydantic settings, environment variables
- **testing** - TDD workflow, pytest patterns, 80% coverage minimum

## Architecture Patterns

- **clean-architecture** - Domain-driven with clear layer separation
- **feature-based** - Organized by feature/module
- **simple** - Minimal structure for small projects

## Example Usage

Once connected, ask your AI assistant:

- "Get the TDD workflow for implementing a user feature"
- "Generate a service template for orders"
- "Show me the naming conventions"
- "Validate this code against architecture rules"
- "Check if my imports follow clean architecture"

## Development

```bash
git clone https://github.com/slahiri/arch.mcp.git
cd arch.mcp
pip install -e ".[dev]"

# Run tests
PYTHONPATH=src pytest tests/ -v

# Lint
ruff check src/
```

## License

MIT
