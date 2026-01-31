# arch-mcp

[![CI](https://github.com/slahiri/arch.mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/slahiri/arch.mcp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/arch-mcp.svg)](https://pypi.org/project/arch-mcp/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Opinionated MCP server for Python API architecture. Build microservices entirely through Claude prompts.

## Quick Start

### 1. Connect to Claude Code

```bash
claude mcp add --transport sse arch-controls https://arch-mcp.sid.sh/sse
```

### 2. Create a Project

Ask Claude:
> "Create a new microservice called product-service"

### 3. Add a Feature

Ask Claude:
> "Add a product feature to my project"

### 4. Run Tests

```bash
cd product-service
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

That's it. Everything else is driven by prompts.

---

## Installation

### Claude Code

```bash
# Remote (recommended)
claude mcp add --transport sse arch-controls https://arch-mcp.sid.sh/sse

# Or local
pip install arch-mcp
claude mcp add arch-controls -- arch-mcp
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

---

## What You Can Do

### Create & Build

| Prompt | What it does |
|--------|--------------|
| "Create a new microservice called order-service" | Scaffolds complete project |
| "Add a user feature to my project" | Creates feature with tests |
| "Generate a service template for payments" | Single file template |

### Get Guidance

| Prompt | What it does |
|--------|--------------|
| "What are the naming conventions?" | Mandatory patterns |
| "Get the TDD workflow for orders" | Step-by-step TDD guide |
| "Show best practices for security" | Category best practices |
| "What's the recommended project structure?" | Architecture patterns |

### Validate Code

| Prompt | What it does |
|--------|--------------|
| "Validate this code against architecture rules" | Check specific code |
| "Check my codebase for violations" | Full architecture check |
| "List all security rules" | Browse rules by category |

---

## Tools Reference

| Tool | Description |
|------|-------------|
| `tool_scaffold_project` | Create new microservice project |
| `tool_scaffold_feature` | Add feature module with tests |
| `tool_get_tdd_workflow` | TDD workflow for a feature |
| `tool_get_naming_conventions` | Mandatory naming patterns |
| `tool_get_file_template` | Generate single file template |
| `tool_validate_code` | Validate code against rules |
| `tool_check_architecture` | Check for layer violations |
| `tool_list_rules` | List rules by category/severity |
| `tool_get_rule` | Get rule details with examples |
| `tool_get_best_practices` | Best practices by category |
| `tool_get_project_structure` | Recommended folder structure |
| `tool_get_architecture_guide` | Complete architecture guide |
| `tool_init_rules` | Initialize custom rules file |

---

## What Gets Enforced

### Naming Conventions

```
ProductCreate, ProductResponse    # Schemas
ProductService                    # Service class
ProductRepository                 # Repository interface
ProductNotFoundError              # Custom exceptions
product_service.py                # File names
```

### Project Structure

```
src/
├── core/           # Configuration
├── shared/         # Shared utilities
├── features/       # Feature modules
│   └── products/
│       ├── schemas.py
│       ├── service.py
│       ├── repository.py
│       ├── router.py
│       └── errors.py
└── main.py
```

### Rules Categories

- **naming** - File, class, function naming
- **structure** - Project organization
- **security** - Secrets, SQL injection, input validation
- **testing** - TDD, 80% coverage, pytest patterns
- **api-design** - Pydantic schemas, dependency injection
- **error-handling** - Custom exceptions
- **logging** - Structured logging
- **configuration** - Pydantic settings

---

## Customizing Rules

Initialize custom rules in your project:

> "Initialize custom architecture rules"

This creates `.arch-mcp/rules.yaml` that you can edit.

---

## Tutorial

See **[docs/TUTORIAL.md](docs/TUTORIAL.md)** for a complete walkthrough.

---

## Development

```bash
git clone https://github.com/slahiri/arch.mcp.git
cd arch.mcp
pip install -e ".[dev]"
pytest
```

## License

MIT
