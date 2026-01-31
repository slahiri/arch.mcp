# arch-mcp

[![CI](https://github.com/slahiri/arch.mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/slahiri/arch.mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/arch-mcp.svg)](https://pypi.org/project/arch-mcp/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Opinionated MCP server for Python API architecture controls. Enforces naming conventions, project structure, and TDD practices.

**[Tutorial: Build a Python Microservice](docs/TUTORIAL.md)** - Step-by-step guide with TDD workflow.

## Installation

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

## Customizing Rules

Rules are defined in YAML and can be customized per-project.

### Initialize custom rules

Ask your AI assistant:
> "Initialize custom architecture rules for this project"

This creates `.arch-mcp/rules.yaml` with all default rules that you can edit.

### Rules search order

1. `ARCH_MCP_RULES` environment variable
2. `.arch-mcp/rules.yaml` in current directory
3. `arch-rules.yaml` in current directory
4. `~/.arch-mcp/rules.yaml` in home directory
5. Package defaults (fallback)

### Example: Adding a custom rule

```yaml
# .arch-mcp/rules.yaml
security:
  - id: no-hardcoded-secrets
    name: No hardcoded secrets
    severity: error
    pattern: "(password|secret|api_key)\\s*=\\s*['\"][^'\"]{8,}['\"]"
    message: Hardcoded secret detected. Use environment variables.

  # Add your custom rule
  - id: require-auth-decorator
    name: Require authentication decorator
    severity: error
    pattern: "@router\\.(get|post|put|delete).*\\n(?!.*@require_auth)"
    message: All endpoints must use @require_auth decorator.
    applies_to: ["**/router.py", "**/routes.py"]
```

## Tools

| Tool | Description |
|------|-------------|
| `tool_scaffold_project` | **Create a new microservice project** |
| `tool_scaffold_feature` | **Add a feature module with tests** |
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
| `tool_init_rules` | Initialize custom rules file in current directory |

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

**Create a project:**
- "Create a new microservice called order-service"
- "Scaffold a product-api project"

**Add features:**
- "Add a product feature to my project"
- "Scaffold a user feature with tests"

**Get guidance:**
- "Get the TDD workflow for implementing payments"
- "Show me the naming conventions"
- "What's the recommended project structure?"

**Validate code:**
- "Validate this code against architecture rules"
- "Check my codebase for architecture violations"

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
