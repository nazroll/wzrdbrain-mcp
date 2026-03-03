# wzrdbrain MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that provides a physics-aware combo generator for wizard-style inline skating, powered by the [`wzrdbrain`](https://pypi.org/project/wzrdbrain/) Python package.

Unlike random trick generators, this server understands skating physics. It models moves as state transitions (direction, edge, stance, weight point), ensuring that the combinations it generates are actually executable and flow naturally.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) for dependency management
- Node.js (optional, for MCP Inspector)

## Installation

```bash
git clone https://github.com/your-username/wzrdbrain-mcp.git
cd wzrdbrain-mcp
uv sync
```

## Client Configuration

### Claude Desktop

Open the configuration file for your operating system:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the following, replacing `<ABSOLUTE_PATH_TO_PROJECT>` with the actual path:

```json
{
  "mcpServers": {
    "wzrdbrain": {
      "command": "uv",
      "args": [
        "--directory",
        "<ABSOLUTE_PATH_TO_PROJECT>",
        "run",
        "mcp-server-wzrdbrain"
      ]
    }
  }
}
```

Restart Claude Desktop. The wzrdbrain tools will appear via the hammer icon in your chat.

### Claude Code

```bash
claude mcp add wzrdbrain -- uv --directory <ABSOLUTE_PATH_TO_PROJECT> run mcp-server-wzrdbrain
```

### Gemini CLI

Add to `.gemini/settings.json` (project-level) or `~/.gemini/settings.json` (user-level), replacing `<ABSOLUTE_PATH_TO_PROJECT>` with the actual path:

```json
{
  "mcpServers": {
    "wzrdbrain": {
      "command": "uv",
      "args": [
        "--directory",
        "<ABSOLUTE_PATH_TO_PROJECT>",
        "run",
        "mcp-server-wzrdbrain"
      ]
    }
  }
}
```

See the [Gemini CLI MCP docs](https://geminicli.com/docs/tools/mcp-server/) for additional options like `timeout` and `env`.

### MCP Inspector

Test the tools locally before connecting to a client:

```bash
npx @modelcontextprotocol/inspector uv run mcp-server-wzrdbrain
```

## Tools

### `generate_skating_combo`

Generates a physics-aware sequence of inline skating tricks.

| Parameter | Type | Default | Range |
|-----------|------|---------|-------|
| `num_tricks` | integer | 3 | 1–20 |

Each line shows the trick name and its entry/exit state (direction/edge/stance/point):

```
1. Front Soul Slide: front/outside/open/all → front/outside/open/all
2. Front Mizu Slide: front/inside/open/all → front/inside/open/all
3. Front Fast Slide: front/outside/open/all → front/outside/open/all
```

### `list_trick_categories`

Returns the available trick categories as a sorted list. No parameters.

```
['base', 'manual', 'pivot', 'slide', 'swivel', 'transition', 'turn']
```

### `get_tricks_by_category`

Lists all tricks in a given category. Case-insensitive.

| Parameter | Type | Required |
|-----------|------|----------|
| `category` | string | yes |

```
Tricks in category:
- Back Predator (Open)
- Back Predator One
- Front Predator (Open)
- Front Predator One
```

Invalid categories return an error listing valid options:
```
Error: Invalid category. Valid categories are: base, manual, pivot, slide, swivel, transition, turn
```

## Prompts

### `skating_practice_routine`

A prompt template that instructs the LLM to generate a 4-trick combo and structure it into a 30-minute practice session:

1. Warm-up (5 minutes)
2. Trick Breakdown & Practice (15 minutes)
3. Combo Execution (5 minutes)
4. Cool-down (5 minutes)

## Error Messages

| Message | Cause |
|---------|-------|
| `Error: num_tricks must be an integer.` | Passed a string, float, or non-integer type |
| `Error: num_tricks must be between 1 and 20.` | Value outside the allowed range |
| `Error: Invalid category. Valid categories are: ...` | Unrecognized category name |
| `Error generating combo: An internal error occurred...` | Unexpected exception from wzrdbrain |

---

## Development

### Setup

```bash
uv sync --extra test
```

### Running Tests

```bash
# All tests
uv run pytest -v

# Single test
uv run pytest tests/test_server.py::TestGenerateSkatingComboHappy::test_default_three_tricks

# Coverage (target: 100%)
uv run pytest --cov=wzrdbrain_mcp --cov-report=term-missing
```

### Project Structure

```
src/wzrdbrain_mcp/server.py   # All MCP tools, prompts, and the entry point
tests/test_server.py           # Full test suite
pyproject.toml                 # Dependencies (pinned with ==) and pytest config
```

### Architecture

- **FastMCP decorated functions** are plain callables — tests call them directly without an MCP client.
- **`wzrdbrain` library** provides two touchpoints: `wzrdbrain.generate_combo()` for combo generation and `MOVES` dict for the trick catalog.
- **State transitions** are modeled as `direction/edge/stance/point`.
- **Input validation** returns error strings, not exceptions. Maintain this pattern for new tools.
- **Output sanitization** validates the structure of `wzrdbrain` responses before formatting.
- **Logging** goes to stderr only. User input is sanitized via `_sanitize_for_log()` before logging to prevent log injection.
- **Dependencies** are pinned with exact versions (`==`) in `pyproject.toml` and locked via `uv.lock`.

### Adding a New Tool

1. Add a `@mcp.tool()` function in `server.py`
2. Validate all inputs (type checks, range bounds) — return error strings for invalid input
3. Sanitize outputs from `wzrdbrain` before returning
4. Log user-supplied values through `_sanitize_for_log()` only
5. Add tests in `tests/test_server.py` — direct calls for happy paths, `unittest.mock.patch` for error paths
6. Verify coverage stays at 100%: `uv run pytest --cov=wzrdbrain_mcp --cov-report=term-missing`
7. Update this README with the new tool's documentation
