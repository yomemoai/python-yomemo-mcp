# yomemoai-mcp

A Model Context Protocol (MCP) server for YoMemoAI, enabling AI assistants to save and retrieve encrypted memories.

## Features

- 🔐 **Secure Storage**: Encrypted memory storage using RSA-OAEP and AES-GCM
- 🏷️ **Categorization**: Organize memories with handles (tags/categories)
- 🔍 **Retrieval**: Query memories by handle or retrieve all memories
- 🚀 **MCP Integration**: Seamlessly integrates with MCP-compatible AI assistants

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- YoMemoAI API key
- RSA private key (PEM format)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yomemoai/python-yomemo-mcp.git
cd python-yomemo-mcp
```

2. Install dependencies using uv:

```bash
uv sync
```

## Configuration

Create a `.env` file in the project root with the following configuration:

```bash
# YoMemoAI MCP Server Configuration

# Your API key from YoMemoAI (required)
MEMO_API_KEY=your_api_key_here

# Path to your private key file (RSA private key in PEM format)
# Default: private.pem
MEMO_PRIVATE_KEY_PATH=private.pem

# Base URL of the YoMemoAI API (optional)
# Default: https://api.yomemo.ai
MEMO_BASE_URL=https://api.yomemo.ai
```

**Important Configuration Notes:**

1. **MEMO_API_KEY** (required): Your YoMemoAI API key. You must obtain this from your YoMemoAI account.

2. **MEMO_PRIVATE_KEY_PATH**: Path to your RSA private key file. The private key should be in PEM format:

   ```
   -----BEGIN PRIVATE KEY-----
   ...
   -----END PRIVATE KEY-----
   ```

   Make sure this file is secure and never commit it to version control.

3. **MEMO_BASE_URL** (optional): The API base URL. Defaults to `https://api.yomemo.ai` if not specified.

## Usage

### Running the MCP Server

After configuration, you can run the MCP server using:

```bash
uv run memo-mcp
```

### Cursor best practice (recommended)

Want the AI to **proactively** save memories when it detects preferences or decisions (not only when you say "remember")?  
Add one rule in Cursor's Rules for AI—see **[CURSOR_RULES.md](./CURSOR_RULES.md)**.

### Debugging the MCP server

You can debug the MCP server with breakpoints in Cursor/VS Code:

1. **Install dev dependency** (includes `debugpy`):

   ```bash
   uv sync --extra dev
   ```

2. **Temporarily point Cursor at the debug entrypoint**  
   In `~/.cursor/mcp.json`, set the server command to (path must be the repo directory):

   ```json
   "yomemoai": {
     "command": "uv",
     "args": ["run", "yomemoai-mcp-debug"],
     "env": { ... },
     "cwd": "/absolute/path/to/python-yomemo-mcp"
   }
   ```

3. **Open the project**  
   Open the `python-yomemo-mcp` folder in Cursor (or the repo with this project inside).

4. **Start the server and attach**  
   - Run & Debug → choose **MCP Server (start and wait for attach)** and start (F5).  
   - Then choose **Attach to MCP Server (attach to 5678)** and start.  
   - After attach, the server continues; use any MCP tool in Cursor to hit your breakpoints.

5. **Restore normal MCP config** when done (e.g. `uv run yomemoai-mcp` or `uvx yomemoai-mcp`).

### Integration with Cursor/Claude Desktop

Add the following configuration to your MCP settings file:

**For Cursor**: `~/.cursor/mcp.json` (or `%APPDATA%\Cursor\User\mcp.json` on Windows)  
**For Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

#### Option 1: Using `uvx` (Recommended - after publishing to PyPI)

If the package is published to PyPI, you can use `uvx` to run it directly. The package provides multiple entry points:

**Using `uvx yomemoai-mcp`** (recommended):

```json
{
  "mcpServers": {
    "yomemoai": {
      "command": "uvx",
      "args": ["yomemoai-mcp"],
      "env": {
        "MEMO_API_KEY": "your_api_key_here",
        "MEMO_PRIVATE_KEY_PATH": "/absolute/path/to/private.pem",
        "MEMO_BASE_URL": "https://api.yomemo.ai"
      }
    }
  }
}
```

**How `uvx` works:**

- `uvx` automatically downloads the package from PyPI (if not already installed)
- It runs the package's entry point script defined in `project.scripts`
- The package name is `yomemoai-mcp`, so `uvx yomemoai-mcp` will automatically use the `yomemoai-mcp` entry point
- The package also provides alternative entry points: `yomemo` and `memo-mcp` (all point to the same server)

**Note**: The package must be published to PyPI before using `uvx`. If the package is not yet published, use Option 2 for local development.

#### Option 2: Using local development setup

For local development or if the package is not yet published, use the `uv --directory` approach:

```json
{
  "mcpServers": {
    "yomemoai": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/yomemoai-mcp",
        "run",
        "yomemoai-mcp"
      ],
      "env": {
        "MEMO_API_KEY": "your_api_key_here",
        "MEMO_PRIVATE_KEY_PATH": "/absolute/path/to/private.pem",
        "MEMO_BASE_URL": "https://api.yomemo.ai"
      }
    }
  }
}
```

**MCP Inspector (when no `cwd`)**  
If the tool has no `cwd` config, put the working directory in `args`, for example:

```json
{
  "command": "uv",
  "args": [
    "--directory",
    "/Users/lvxiang/work/shared/github/memo/python-yomemo-mcp",
    "run",
    "yomemoai-mcp"
  ],
  "env": {
    "MEMO_API_KEY": "your_api_key_here",
    "MEMO_PRIVATE_KEY_PATH": "private.pem",
    "MEMO_BASE_URL": "https://api.yomemo.ai"
  }
}
```

Replace the path after `--directory` with the **absolute path** to this project on your machine.

**Important Notes:**

- **For Option 1 (`uvx`)**: The package must be published to PyPI. `uvx` will automatically handle installation and execution.
- **For Option 2 (local) / MCP Inspector**: Replace the path after `--directory` with the **absolute path** to this repo (e.g. `/Users/you/work/python-yomemo-mcp`). No `cwd` field is needed.
- Replace `MEMO_PRIVATE_KEY_PATH` with a path relative to the project dir (e.g. `private.pem`) or an absolute path to your private key file.
- The `env` section in the MCP config will override any `.env` file in the project directory.
- After updating the MCP config, restart Cursor/Claude Desktop / MCP Inspector for changes to take effect.

### Available Tools

#### `save_memory`

Store important information, user preferences, or conversation context as a permanent memory.

**Parameters:**

- `content` (required): The actual text/information to be remembered
- `handle` (optional): A short, unique category or tag (e.g., 'work', 'personal', 'project-x'). Defaults to 'general'
- `description` (optional): A brief summary of what this memory is about

#### `load_memories`

Retrieve previously stored memories with optional pagination and lightweight modes to reduce token usage.

**Parameters:**

- `handle` (optional): Filter memories by category. If not specified, returns memories across all handles.
- `limit` (default 20): Number of memories per page. Use with `cursor` for pagination.
- `cursor` (optional): Pagination cursor from the previous response's "Next cursor" line. Omit for the first page.
- `mode`: What to return:
  - `"summary"` (default): Description + metadata + id/handle/idempotent_key only (no decrypted content). Use first to scan and decide.
  - `"metadata"`: Only id, handle, created_at, metadata. Smallest payload.
  - `"full"`: Full decrypted content. Use after you need details for the current page (same cursor/limit as the summary call).

**Recommended flow:** Call with `mode='summary'` or `mode='metadata'` first; use the returned "Next cursor" to paginate or call again with `mode='full'` and the same cursor to load full content for that page.

## Development

### Project Structure

```
yomemoai-mcp/
├── src/
│   └── yomemoai_mcp/
│       ├── __init__.py
│       ├── server.py      # MCP server implementation
│       ├── client.py      # YoMemoAI API client
│       └── py.typed       # Type hints marker
├── pyproject.toml         # Project configuration
├── uv.lock                # Dependency lock file
└── README.md
```

### Dependencies

- `cryptography`: For encryption/decryption operations
- `fastmcp`: FastMCP framework for MCP servers
- `mcp`: Model Context Protocol SDK
- `python-dotenv`: Environment variable management
- `requests`: HTTP client for API calls

## Security Notes

- **Never commit** your `.env` file or private key files to version control
- Keep your private key secure and never share it
- The `.env` file is already included in `.gitignore`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Support

For issues and questions, please open an issue on the repository.
