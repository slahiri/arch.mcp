# arch-mcp

[![CI](https://github.com/slahiri/arch.mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/slahiri/arch.mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/arch-mcp.svg)](https://pypi.org/project/arch-mcp/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server for Python API architecture controls. Validates code against architecture rules and best practices.

## Quick Start

### Option 1: Hosted (Recommended)

No install needed. Just add to your config:

**Claude Code:**
```bash
claude mcp add arch-controls --url https://arch-mcp.sid.sh/sse
```

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "arch-controls": {
      "url": "https://arch-mcp.sid.sh/sse"
    }
  }
}
```

### Option 2: Local via uvx

Run locally without installing:

**Claude Code:**
```bash
claude mcp add arch-controls -- uvx arch-mcp
```

**Cursor** (`.cursor/mcp.json`):
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

### Option 3: Local Install

```bash
pip install arch-mcp
```

**Claude Code:**
```bash
claude mcp add arch-controls -- arch-mcp
```

**Cursor** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "arch-controls": {
      "command": "arch-mcp"
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

## Rule Categories

- **security** - Secrets management, SQL injection prevention, input validation
- **data-access** - Repository pattern, async database operations
- **error-handling** - Custom exceptions, specific exception catches
- **api-design** - Pydantic schemas, dependency injection
- **logging** - Structured logging, no print statements
- **configuration** - Pydantic settings, environment variables
- **testing** - Pytest patterns, fixtures

## Architecture Patterns

- **clean-architecture** - Domain-driven with clear layer separation
- **feature-based** - Organized by feature/module
- **simple** - Minimal structure for small projects

## Example Usage

Once connected, ask your AI assistant:

- "List all security rules"
- "Validate this code against architecture rules"
- "Show me the recommended project structure"
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
