# MCP Multi-Server Client

A simple Python client built with **LangChain MCP Adapters** that connects to multiple MCP servers and allows an LLM to discover and use their tools automatically.

## Features

- Connect to multiple MCP servers
- Support for both **stdio** and **HTTP** transports
- Automatic tool discovery
- LLM tool calling with LangChain
- Easy to add or remove MCP servers

## Tech Stack

- Python
- LangChain
- LangChain MCP Adapters
- FastMCP
- Groq LLM

---

## Installation

```bash
git clone https://github.com/Maaz708/simple_mcp_client_test

cd mcp-client

```

or

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python client.py
```

---

# Connecting Multiple MCP Servers

The client supports connecting to multiple MCP servers simultaneously.

Example:

```python
SERVERS = {
    "math": {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "path/to/math_server.py"
        ]
    },

    "expense": {
        "transport": "streamable_http",
        "url": "https://your-server.fastmcp.app/mcp"
    },

    "filesystem": {
        "transport": "stdio",
        "command": "python",
        "args": [
            "filesystem_server.py"
        ]
    }
}
```

Then initialize the client:

```python
client = MultiServerMCPClient(SERVERS)

tools = await client.get_tools()
```

The client automatically loads tools from every connected server, making them available to the LLM for tool calling.

---

## Supported Transports

- **stdio** – Local MCP servers
- **streamable_http** – Remote MCP servers

---

