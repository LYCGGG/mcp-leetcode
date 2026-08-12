# MCP LeetCode

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-SDK-green.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于 Python 的 LeetCode MCP Server，支持 leetcode.com 和 leetcode.cn。

## 功能特性

- 🌐 **双站点支持** - leetcode.com (国际版) & leetcode.cn (中国版)
- 🔍 **问题查询** - 搜索、筛选、获取题目详情
- 👤 **用户数据** - 个人资料、提交记录、做题进度、竞赛信息
- 💻 **代码执行** - 运行测试、提交代码
- 📝 **笔记管理** - 增删改查 (仅中国版)
- ⚡ **智能缓存** - 内置缓存，减少 API 调用
- 🛡️ **类型安全** - 完整的 Pydantic v2 类型定义

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/LYCGGG/mcp-leetcode.git
cd mcp-leetcode

# 安装依赖
pip install -e .
```

### 配置

```bash
cp config.example.yaml config.yaml
# 编辑 config.yaml 填入你的配置
```

### 运行

```bash
python -m leetcode_mcp.server
```

## MCP 客户端配置

### opencode

```json
{
  "mcp": {
    "leetcode": {
      "type": "local",
      "enabled": true,
      "command": ["python", "-m", "leetcode_mcp.server"],
      "env": {
        "LEETCODE_SITE": "cn",
        "LEETCODE_SESSION": "你的session值",
        "LEETCODE_CSRF": "你的csrf值"
      }
    }
  }
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "leetcode": {
      "command": "python",
      "args": ["-m", "leetcode_mcp.server"],
      "env": {
        "LEETCODE_SITE": "cn",
        "LEETCODE_SESSION": "你的session值",
        "LEETCODE_CSRF": "你的csrf值"
      }
    }
  }
}
```

### VS Code

```json
{
  "mcp": {
    "servers": {
      "leetcode": {
        "command": "python",
        "args": ["-m", "leetcode_mcp.server"],
        "env": {
          "LEETCODE_SITE": "cn"
        }
      }
    }
  }
}
```

## 可用工具

### 问题相关

| 工具 | 说明 |
|------|------|
| `get_daily_challenge` | 获取每日一题 |
| `get_problem` | 获取题目详情 |
| `search_problems` | 搜索题目 (支持标签、难度、关键词筛选) |
| `list_problem_solutions` | 获取题解列表 |

### 用户相关

| 工具 | 说明 |
|------|------|
| `get_user_profile` | 获取用户信息 |
| `get_recent_ac_submissions` | 获取最近通过的提交 |
| `get_user_contest_ranking` | 获取竞赛排名 |

### 代码执行

| 工具 | 说明 |
|------|------|
| `run_code` | 运行代码 (需要认证) |
| `submit_solution` | 提交代码 (需要认证) |

### 笔记管理 (仅中国版)

| 工具 | 说明 |
|------|------|
| `get_notes` | 获取笔记 |
| `create_note` | 创建笔记 |
| `update_note` | 更新笔记 |

## 获取 Cookie

1. 登录 [leetcode.cn](https://leetcode.cn) 或 [leetcode.com](https://leetcode.com)
2. 打开浏览器开发者工具 (F12)
3. 切换到 Application/存储 标签
4. 找到 Cookie，复制 `LEETCODE_SESSION` 和 `csrftoken`

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check src/
```

## 文档

- [使用指南](docs/USAGE.md)
- [设计文档](docs/DESIGN.md)

## License

MIT
