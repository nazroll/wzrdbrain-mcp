# AGENTS.md

This file provides context, commands, and architectural guidance for any AI coding assistants (like Gemini, Claude, Cursor, Copilot, etc.) working within this repository.

## Project Overview

An MCP server exposing the `wzrdbrain` Python package (physics-aware inline skating combo generator) as MCP tools and prompts. Built with FastMCP. Uses `uv` for dependency management.

## Commands

```bash
# Install / sync dependencies
uv sync

# Install with test dependencies
uv sync --extra test

# Run the MCP server
uv run mcp-server-wzrdbrain

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run mcp-server-wzrdbrain

# Run all tests
uv run pytest -v

# Run a single test
uv run pytest tests/test_server.py::TestGenerateSkatingComboHappy::test_default_three_tricks

# Run tests with coverage
uv run pytest --cov=wzrdbrain_mcp --cov-report=term-missing
```

## Architecture

Single-module server at `src/wzrdbrain_mcp/server.py`. All MCP tools are plain decorated functions (`@mcp.tool()`) that can be called directly in tests without an MCP client. The server wraps the `wzrdbrain` library which models skating moves as state transitions (direction/edge/stance/point).

Key patterns:
- **Input validation** happens before calling `wzrdbrain` — type checks and range bounds return error strings, not exceptions
- **Output sanitization** — raw `wzrdbrain` responses are validated for expected dict structure before formatting
- **`_sanitize_for_log()`** strips non-printable chars and truncates before logging user input
- **All logging goes to stderr** to keep stdout clean for MCP protocol communication
- **Dependencies are pinned with exact versions** (`==`) in `pyproject.toml`

## Testing

Tests are in `tests/test_server.py`. They call the tool functions directly and use `unittest.mock.patch` on `wzrdbrain_mcp.server.wzrdbrain.generate_combo` and `wzrdbrain_mcp.server.MOVES` for error path coverage. Current coverage: 100%.
