
# My First MCP Server — Setup Journey

A step-by-step log of building and connecting my first [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) server to Claude Desktop, using the official Python SDK. This README documents exactly what was done, in order, including the issues hit along the way.

Built on: **macOS Monterey 12.7.6**, Intel i5, 8GB RAM (2015 MacBook Pro).

---

## What is MCP

MCP lets an app like Claude Desktop call out to a local program (a "server") for tools and live data, instead of relying only on the model's built-in knowledge. This project builds a simple calculator server and connects it to Claude Desktop as a working example.

SDK used: [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)

---

## Steps followed

### 1. Install `uv` (Python package/project manager)

`uv` wasn't installed, so:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv --version
```

### 2. Create the project

```bash
mkdir mcp-test && cd mcp-test
uv init
uv add "mcp[cli]"
```

**Issue hit:** `uv init` defaulted `requires-python` to `>=3.14`, a version with no prebuilt wheel for the `cryptography` dependency — `uv add` sat compiling it from source for a very long time.

**Fix:** pin the project to a more compatible Python version:

```bash
sed -i '' 's/requires-python = ">=3.14"/requires-python = ">=3.10"/' pyproject.toml
rm -rf .venv
uv venv --python 3.12
uv add "mcp[cli]"
```

This installed cleanly using a prebuilt wheel.

### 3. Write the server

Created `calculator_server.py` using `mcp.server.MCPServer`, exposing calculator functions as **tools** (`add`, `subtract`, `multiply`, `divide`, `power`, `square_root`, `percentage`) and a small in-memory calculation log as a **resource** (`history://recent`), so tool calls and resource reads could both be demonstrated.

### 4. Test locally with the MCP Inspector

```bash
uv run mcp dev calculator_server.py
```

**Issue hit:** `npx not found` — the Inspector needs Node.js, which wasn't installed.

**Fix:** installed Node via `nvm` (chosen over Homebrew, since Homebrew's latest Node bottle isn't well supported on macOS Monterey and risked a slow/failing source build):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.zshrc
nvm install 20
nvm use 20
```

Reran `uv run mcp dev calculator_server.py` — it started the Inspector proxy and printed a local URL with an auth token. Opened that URL in the browser and confirmed:
- **Tools tab** → called `multiply(6, 7)` → got `42`
- **Resources tab** → opened `history://recent` → saw the call logged

### 5. Connect the server to Claude Desktop

In Claude Desktop: **Settings → Developer → Local MCP servers → Edit Config**.

**Issue hit:** manually opening `claude_desktop_config.json` via terminal initially showed an unrelated app-preferences file, not the MCP config — resolved by using the in-app **Edit Config** button instead of guessing the file path, since it opens the correct file for the installed build.

Added:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "/Users/<you>/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/<you>/Documents/mcp-test",
        "run",
        "calculator_server.py"
      ]
    }
  }
}
```

Used the full path to `uv` (from `which uv`) since Claude Desktop's process doesn't inherit the terminal shell's PATH.

### 6. Verify it's actually working

In **Settings → Developer**, the `calculator` server showed status **running**.

In a chat, confirmed the `calculator` toggle was on under the "+" → connectors menu, then asked Claude a question it could only answer using the tool's live state:

> "What's in my calculator history?"

First attempt returned no history — because the earlier questions asked ("what's 84 divided by 12") were simple enough that Claude just computed them mentally instead of calling the tool. Asking more explicitly:

> "Use the calculator tool for 84 divided by 12, and 15% of 200."

produced a response tagged **"used calculator integration"** in the UI — confirming the tool call was real, not just model math.

---

## Result

A working local MCP server with 7 tools and 1 resource, connected to Claude Desktop, verified end-to-end via real tool invocation (not just Claude's own arithmetic).

## Project structure

```
mcp-test/
├── calculator_server.py   # the MCP server
├── pyproject.toml           # project + dependency config (Python >=3.10)
├── uv.lock                   # locked dependency versions
└── README.md                 # this file
```

## Reference

- SDK: https://github.com/modelcontextprotocol/python-sdk
- Docs: https://py.sdk.modelcontextprotocol.io/
