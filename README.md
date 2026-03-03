# WzrdBrain MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that provides a physics-aware combo generator for wizard-style inline skating, powered by the [`wzrdbrain`](https://pypi.org/project/wzrdbrain/) Python package.

Unlike random trick generators, this server understands skating physics. It models moves as state transitions (direction, edge, stance, weight point), ensuring that the combinations it generates for the LLM are actually executable and flow naturally.

## Features

This server exposes the following MCP Tools to your AI client:

### Tools
*   **`generate_skating_combo`**
    *   Generates a sequence of inline skating tricks that are physically possible to chain together.
    *   *Parameters:* `num_tricks` (Integer, default: 3, max: 20)
    *   *Output:* Each move includes full state transitions showing direction, edge, stance, and weight point. Example:
        ```
        1. Back Predator (Open): back/center/open/toe → back/center/open/toe
        ```
*   **`list_trick_categories`**
    *   Returns the available categories of tricks (e.g., `base`, `pivot`, `slide`, `turn`, `transition`).
*   **`get_tricks_by_category`**
    *   Looks up specific tricks within a given category.
    *   *Parameters:* `category` (String)

### Prompts
*   **`skating_practice_routine`**
    *   A pre-defined prompt template that asks the LLM to generate a combo and structure it into a detailed 30-minute practice session, including warm-ups and trick breakdowns.

## Installation & Setup

This project uses [uv](https://docs.astral.sh/uv/) for incredibly fast dependency management and virtual environments.

1.  **Ensure you have `uv` installed:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2.  **Clone this repository:**
    ```bash
    git clone https://github.com/your-username/wzrdbrain-mcp.git
    cd wzrdbrain-mcp
    ```
3.  **Sync the project and build the executable:**
    ```bash
    uv sync
    ```

## Testing Locally

You can test the tools and prompts locally using the official MCP Inspector before hooking it up to an AI client:

```bash
npx @modelcontextprotocol/inspector uv run mcp-server-wzrdbrain
```

## Client Configuration Guide (Claude Desktop)

To use this server with Claude Desktop, you need to add it to your client's configuration file.

Open the configuration file for your operating system:
*   **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
*   **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the following configuration, making sure to replace `<ABSOLUTE_PATH_TO_PROJECT>` with the actual path to where you cloned this repository on your machine:

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

Restart Claude Desktop. You will now see the `wzrdbrain` tools available via the hammer icon (🛠️) in your chat!

## Architecture & Security

This server was built with a strong focus on defensive programming and system stability:
*   **Input Validation:** Hard bounds are placed on the number of tricks requested (1-20). Categories are strictly validated against an internal allowlist before querying the underlying package.
*   **Output Sanitization:** Raw stack traces and unexpected internal schema changes from the `wzrdbrain` library are caught and sanitized before being returned to the LLM.
*   **Supply Chain Security:** Dependencies are pinned with exact versions (`==`) in `pyproject.toml` and locked via `uv.lock` for reproducible builds.
*   **Safe Logging:** Internal logging is routed strictly to `stderr` and strips non-printable control characters from user input to prevent log injection.
