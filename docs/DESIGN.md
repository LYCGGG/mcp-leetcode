# MCP LeetCode 设计文档

## 1. 项目概述

MCP LeetCode 是一个基于 Python MCP SDK 的 LeetCode 集成服务，让 AI 助手能够直接与 LeetCode 交互，获取题目、提交代码、管理笔记等。

### 1.1 设计目标

- **功能完整**：覆盖 LeetCode 核心 API
- **类型安全**：Pydantic v2 完整类型定义
- **异步优先**：全异步架构，高性能
- **易于扩展**：模块化设计，便于添加新功能

### 1.2 与现有实现对比

| 特性 | jinzcdev (TypeScript) | 本项目 (Python) |
|------|----------------------|-----------------|
| 类型安全 | 部分 any | Pydantic 强类型 |
| 缓存 | 无 | 内置 LRU 缓存 |
| 异步 | 部分 | 全异步 |
| 错误处理 | 基础 | 统一异常类 |
| 配置 | 环境变量 | YAML + 环境变量 |

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Client (IDE)                      │
└─────────────────────────┬───────────────────────────────┘
                          │ stdio / http
┌─────────────────────────▼───────────────────────────────┐
│                   MCP Server Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ problem  │ │   user   │ │submission│ │   note   │   │
│  │  tools   │ │  tools   │ │  tools   │ │  tools   │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼───────┘
        │             │             │             │
┌───────▼─────────────▼─────────────▼─────────────▼───────┐
│                   Service Layer                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              LeetCodeClient                      │   │
│  │  - GraphQL 查询                                   │   │
│  │  - HTTP 请求                                      │   │
│  │  - 认证管理                                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   Cache Layer                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │              LRUCache                            │   │
│  │  - 内存缓存                                       │   │
│  │  - TTL 过期                                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
mcp-leetcode/
├── src/
│   └── leetcode_mcp/
│       ├── __init__.py          # 版本信息
│       ├── server.py            # MCP Server 入口
│       ├── config.py            # 配置管理
│       ├── client.py            # HTTP 客户端
│       ├── models.py            # Pydantic 数据模型
│       ├── exceptions.py        # 自定义异常
│       ├── cache.py             # 缓存工具
│       ├── graphql/
│       │   ├── __init__.py
│       │   ├── queries.py       # GraphQL 查询语句
│       │   └── mutations.py     # GraphQL 变更语句
│       └── tools/
│           ├── __init__.py
│           ├── problem.py       # 问题相关工具
│           ├── user.py          # 用户相关工具
│           ├── submission.py    # 提交相关工具
│           ├── solution.py      # 题解相关工具
│           └── note.py          # 笔记相关工具
├── tests/
├── docs/
│   └── DESIGN.md
├── config.example.yaml
├── pyproject.toml
└── README.md
```

## 3. 模块设计

### 3.1 配置管理 (config.py)

支持两种配置方式：
1. **配置文件**：`config.yaml`
2. **环境变量**：优先级高于配置文件

```python
# 环境变量映射
LEETCODE_SITE    → site
LEETCODE_SESSION → auth.session
LEETCODE_CSRF    → auth.csrf_token
```

### 3.2 HTTP 客户端 (client.py)

- 基于 `httpx.AsyncClient`
- 支持 GraphQL 查询
- 自动处理认证头
- 请求日志记录

### 3.3 数据模型 (models.py)

使用 Pydantic v2 定义：

```python
class Problem(BaseModel):
    title_slug: str
    question_id: int
    title: str
    content: str
    difficulty: Difficulty
    topic_tags: list[Tag]
    # ...

class SearchResult(BaseModel):
    total: int
    has_more: bool
    problems: list[Problem]
```

### 3.4 工具层 (tools/)

每个工具模块包含：
- 工具注册函数
- 参数验证 (Pydantic)
- 调用服务层
- 返回格式化结果

### 3.5 缓存层 (cache.py)

```python
@cached(ttl=300)
async def get_problem(title_slug: str) -> Problem:
    ...
```

## 4. API 设计

### 4.1 GraphQL 查询

主要查询语句：

- `problemDetail` - 题目详情
- `problemsetQuestionList` - 题目列表
- `userProfile` - 用户信息
- `submissionList` - 提交记录
- `questionSolutionArticles` - 题解列表

### 4.2 认证流程

1. 从浏览器获取 `LEETCODE_SESSION` 和 `csrftoken`
2. 设置到请求头 `Cookie` 和 `x-csrftoken`
3. 部分 API 需要认证 (用户数据、提交等)

## 5. 错误处理

### 5.1 异常类型

```python
class LeetCodeError(Exception):
    """Base exception"""

class AuthenticationError(LeetCodeError):
    """认证失败"""

class NotFoundError(LeetCodeError):
    """资源不存在"""

class RateLimitError(LeetCodeError):
    """请求频率限制"""
```

### 5.2 错误响应格式

```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Session expired"
  }
}
```

## 6. 开发计划

### Phase 1: 基础框架 ✓
- [x] 项目结构
- [x] 配置管理
- [x] 基础客户端

### Phase 2: 核心功能
- [ ] 数据模型
- [ ] 问题工具
- [ ] 用户工具

### Phase 3: 高级功能
- [ ] 代码执行
- [ ] 笔记管理
- [ ] 缓存优化

### Phase 4: 测试与文档
- [ ] 单元测试
- [ ] 集成测试
- [ ] 完善文档
