# Project Description for GitHub/PyPI

**yomemoai-mcp** is a Model Context Protocol (MCP) server that enables AI assistants like Claude and Cursor to seamlessly save and retrieve encrypted memories through YoMemoAI's secure storage platform.

## Key Features

- **End-to-End Encryption**: All memories are encrypted client-side using RSA-OAEP and AES-GCM before being stored, ensuring your data remains private even from the service provider
- **Persistent Memory**: AI assistants can remember important information, user preferences, and conversation context across sessions
- **Organized Storage**: Memories can be categorized using handles (tags/categories) for easy retrieval and organization
- **MCP Integration**: Built on the Model Context Protocol standard, making it compatible with any MCP-enabled AI assistant
- **Easy Installation**: Available on PyPI and can be installed with a single command: `uvx yomemoai-mcp`

## Use Cases

- Save important user preferences and context that AI assistants should remember
- Store conversation history and key information for future reference
- Organize memories by topics, projects, or categories using handles
- Enable AI assistants to maintain long-term memory across multiple sessions

## Technical Highlights

- Hybrid encryption architecture (RSA + AES-GCM) for secure data storage
- FastMCP framework for efficient MCP server implementation
- Type-safe Python implementation with full type hints
- Simple configuration via environment variables

Perfect for developers and users who want to give their AI assistants persistent, encrypted memory capabilities.
