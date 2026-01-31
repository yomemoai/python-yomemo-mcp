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

**Important Notes:**

- **For Option 1 (`uvx`)**: The package must be published to PyPI. `uvx` will automatically handle installation and execution.
- **For Option 2 (local)**: Replace `/absolute/path/to/yomemoai-mcp` with the **absolute path** to this repository on your system
- Replace `/absolute/path/to/private.pem` with the **absolute path** to your private key file
- The `env` section in the MCP config will override any `.env` file in the project directory
- After updating the MCP config, restart Cursor/Claude Desktop for changes to take effect

### Available Tools

#### `save_memory`

Store important information, user preferences, or conversation context as a permanent memory.

**Parameters:**

- `content` (required): The actual text/information to be remembered
- `handle` (optional): A short, unique category or tag (e.g., 'work', 'personal', 'project-x'). Defaults to 'general'
- `description` (optional): A brief summary of what this memory is about

#### `load_memories`

Retrieve previously stored memories or context.

**Parameters:**

- `handle` (optional): Filter memories by category. If not specified, returns all memories

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
