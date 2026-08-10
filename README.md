# MCP LeetCode

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-SDK-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A feature-rich LeetCode MCP Server written in Python, supporting both leetcode.com and leetcode.cn.

## Features

- 🌐 **Dual Site Support** - leetcode.com (Global) & leetcode.cn (China)
- 🔍 **Problem Query** - Search, filter, and get problem details
- 👤 **User Data** - Profile, submissions, progress, contest info
- 💻 **Code Execution** - Run and submit code
- 📝 **Notes Management** - CRUD operations (CN only)
- ⚡ **Smart Caching** - Reduce API calls with built-in cache
- 🛡️ **Type Safe** - Full Pydantic v2 type definitions

## Quick Start

### Installation

```bash
pip install mcp-leetcode
```

### Configuration

```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your settings
```

### Run

```bash
mcp-leetcode
```

## MCP Client Configuration

### Claude Desktop

```json
{
  "mcpServers": {
    "leetcode": {
      "command": "mcp-leetcode",
      "env": {
        "LEETCODE_SITE": "cn",
        "LEETCODE_SESSION": "your_session_cookie",
        "LEETCODE_CSRF": "your_csrf_token"
      }
    }
  }
}
```

### VS Code (Copilot)

```json
{
  "mcp": {
    "servers": {
      "leetcode": {
        "command": "mcp-leetcode",
        "env": {
          "LEETCODE_SITE": "cn"
        }
      }
    }
  }
}
```

## Available Tools

### Problems

| Tool | Description |
|------|-------------|
| `get_daily_challenge` | Get today's daily challenge |
| `get_problem` | Get problem details by slug |
| `search_problems` | Search with filters (tags, difficulty, keywords) |
| `get_problem_solutions` | Get community solutions |

### Users

| Tool | Description |
|------|-------------|
| `get_user_profile` | Get user profile information |
| `get_user_submissions` | Get submission history |
| `get_user_progress` | Get problem-solving progress |
| `get_contest_info` | Get contest ranking info |

### Code Execution

| Tool | Description |
|------|-------------|
| `run_code` | Run code with test cases |
| `submit_solution` | Submit code to LeetCode |

### Notes (CN only)

| Tool | Description |
|------|-------------|
| `get_notes` | Get user notes |
| `create_note` | Create a new note |
| `update_note` | Update existing note |

## Development

```bash
# Clone
git clone https://github.com/LYCGGG/mcp-leetcode.git
cd mcp-leetcode

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/
```

## License

MIT
