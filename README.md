# arch-mcp

MCP server for Python API architecture controls. Built with FastMCP 3.0.

## Installation

```bash
pip install -e .
```

## Usage

### Run the server

```bash
arch-mcp
# or
python -m arch_mcp.server
```

### Configure in Claude Code

```bash
claude mcp add arch-controls -- arch-mcp
```

### Configure in Cursor

Add to `.cursor/mcp.json`:

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
| `list_rules` | List architecture rules |
| `get_rule` | Get rule details with examples |
| `validate_code` | Validate code against rules |
| `get_project_structure` | Get recommended folder structure |
| `get_best_practices` | Get best practices by category |
| `check_architecture` | Check codebase consistency |
| `get_architecture_guide` | Complete architecture guide |

## Rule Categories

- `security` - Secrets, SQL injection, input validation
- `data-access` - Repository pattern, async DB
- `error-handling` - Custom exceptions, specific catches
- `api-design` - Pydantic schemas, dependency injection
- `logging` - Structured logging, no print
- `configuration` - Pydantic settings
- `testing` - Pytest patterns

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
```

## Sources

- [FastMCP](https://github.com/jlowin/fastmcp)
- [gofastmcp.com](https://gofastmcp.com)
- [MCP Protocol](https://modelcontextprotocol.io)
