# arch-mcp

MCP server for Python API architecture controls. Validates code against architecture rules and best practices. Built with FastMCP 3.0.

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/slahiri/arch.mcp.git
cd arch.mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e .
```

### 2. Connect to Your IDE

#### Claude Code

```bash
claude mcp add arch-controls -- arch-mcp
```

Or add manually to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "arch-controls": {
      "command": "/path/to/arch.mcp/venv/bin/arch-mcp"
    }
  }
}
```

#### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "arch-controls": {
      "command": "/path/to/arch.mcp/venv/bin/arch-mcp"
    }
  }
}
```

Or add globally to `~/.cursor/mcp.json`.

> **Note**: Replace `/path/to/arch.mcp` with the actual path where you cloned the repository.

### 3. Verify Connection

In Claude Code, run:
```bash
claude mcp list
```

In Cursor, open the MCP panel to see connected servers.

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

## Resources

| Resource | Description |
|----------|-------------|
| `arch://rules` | All architecture rules as JSON |
| `arch://categories` | List of rule categories |
| `arch://guide` | Complete architecture guide |

## Rule Categories

- **security** - Secrets management, SQL injection prevention, input validation
- **data-access** - Repository pattern, async database operations
- **error-handling** - Custom exceptions, specific exception catches
- **api-design** - Pydantic schemas, dependency injection
- **logging** - Structured logging, no print statements
- **configuration** - Pydantic settings, environment variables
- **testing** - Pytest patterns, fixtures

## Architecture Patterns

The server supports three architecture patterns:

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
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
PYTHONPATH=src pytest tests/ -v

# Lint
ruff check src/
```

## Troubleshooting

### Server not connecting

1. Ensure the virtual environment is activated when installing
2. Use absolute paths in MCP config files
3. Check that `arch-mcp` is in your PATH: `which arch-mcp`

### Command not found

If `arch-mcp` isn't found, use the full path:
```bash
/path/to/arch.mcp/venv/bin/arch-mcp
```

### Cursor not detecting server

1. Restart Cursor after adding MCP config
2. Check `.cursor/mcp.json` syntax is valid JSON
3. Ensure the command path is absolute

## License

MIT

## Links

- [FastMCP](https://github.com/jlowin/fastmcp)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Claude Code](https://docs.anthropic.com/claude-code)
- [Cursor](https://cursor.sh)
