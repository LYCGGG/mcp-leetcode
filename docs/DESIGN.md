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
┌──────────────────────────────────────────────────────────┐
│                  MCP Client (IDE/AI)                      │
└──────────────────────┬───────────────────────────────────┘
                       │ stdio
┌──────────────────────▼───────────────────────────────────┐
│              MCP Tools & Resources Layer                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ problem  │ │   user   │ │submission│ │  note    │    │
│  │  tools   │ │  tools   │ │  tools   │ │  tools   │    │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘    │
│       │  registry_base.py (模板方法: 按 site/auth 分组)   │
└───────┼─────────────┼─────────────┼─────────────┼────────┘
        │             │             │             │
┌───────▼─────────────▼─────────────▼─────────────▼────────┐
│                  Service Layer                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  LeetCodeBaseService (ABC)                          │ │
│  │    ├── LeetCodeCNService     (leetcode.cn)          │ │
│  │    └── LeetCodeGlobalService (leetcode.com)         │ │
│  │                                                     │ │
│  │  LeetCodeServiceFactory.create(site, session)       │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│              Infrastructure Layer                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ client.py│ │graphql/  │ │ models.py│ │ cache.py │    │
│  │ httpx    │ │ queries  │ │ Pydantic │ │  LRU     │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
src/leetcode_mcp/
├── __init__.py                  # 版本信息
├── server.py                    # MCP Server 入口 (FastMCP)
├── config.py                    # YAML + 环境变量配置
├── constants.py                 # 语言/分类/标签常量
├── exceptions.py                # 统一异常类
├── client.py                    # httpx 异步 HTTP 客户端
├── models.py                    # Pydantic 工具参数模型
├── cache.py                     # TTL LRU 缓存 + @cached 装饰器
│
├── leetcode/
│   ├── base_service.py          # ABC: 定义 ~20 个抽象方法
│   ├── cn_service.py            # leetcode.cn 实现
│   ├── global_service.py        # leetcode.com 实现
│   └── service_factory.py       # 工厂方法
│
├── graphql/
│   ├── cn/                      # CN 站 GraphQL 查询
│   │   ├── search_problems.py
│   │   ├── solution_articles.py
│   │   ├── solution_detail.py
│   │   └── note_queries.py
│   └── lc_global/               # Global 站 GraphQL 查询
│       ├── search_problems.py
│       ├── solution_articles.py
│       └── solution_detail.py
│
├── tools/
│   ├── registry_base.py         # 模板方法基类 (6 个 hook)
│   ├── problem_tools.py         # get_daily_challenge, get_problem, search_problems
│   ├── user_tools.py            # get_user_profile, get_user_status, submissions 等
│   ├── submission_tools.py      # run_code, submit_solution
│   ├── solution_tools.py        # list_problem_solutions, get_problem_solution
│   └── note_tools.py            # search_notes, get_note, create_note, update_note
│
└── resources/
    ├── resource_registry.py     # 资源注册基类
    ├── problem_resources.py     # categories, tags, langs, problem-detail
    └── solution_resources.py    # solution://{slug|topicId}
```

## 3. 模块设计

### 3.1 配置管理 (config.py)

支持两种配置方式，优先级：环境变量 > YAML 文件 > 默认值

```python
# 环境变量映射
LEETCODE_SITE    → site ("cn" 或 "global")
LEETCODE_SESSION → auth.session
LEETCODE_CSRF    → auth.csrf_token
LEETCODE_LOG_LEVEL → logging.level
```

### 3.2 HTTP 客户端 (client.py)

- 基于 `httpx.AsyncClient`
- `graphql()` — 发送 GraphQL 查询，自动处理认证头和错误
- `post_json()` / `get_json()` — REST 请求
- `poll_check()` — 轮询提交结果，支持超时和 429 退避

### 3.3 服务层 (leetcode/)

**工厂模式**：`service_factory.create_service(config)` 根据 `site` 配置创建对应服务

**策略模式**：`LeetCodeBaseService` (ABC) 定义接口，CN/Global 各自实现

关键差异：
- CN 用 `todayRecord` 获取每日一题，Global 用 `activeDailyCodingChallengeQuestion`
- CN 用 `userSlug` 参数，Global 用 `username`
- CN 支持笔记功能，Global 不支持
- CN 的题解用 `slug` 标识，Global 用 `topicId`

### 3.4 工具注册 (tools/registry_base.py)

**模板方法模式**，按 (站点 × 认证) 矩阵分组注册：

```
register()
  → registerCommon()                        // 无认证，两站通用
  → isCN() ? registerChina() : registerGlobal()  // 无认证，站点特定
  → if authenticated:
      registerAuthenticatedCommon()         // 有认证，两站通用
      isCN() ? registerAuthenticatedChina() : registerAuthenticatedGlobal()
```

### 3.5 缓存层 (cache.py)

```python
@cached(ttl=300)
async def get_problem(title_slug: str) -> dict:
    ...
```

## 4. MCP 工具列表

### 无认证工具（两站通用）

| 工具 | 说明 |
|------|------|
| `get_daily_challenge` | 获取每日一题 |
| `get_problem` | 获取题目详情（简化版） |
| `search_problems` | 按标签/难度/关键词搜索题目 |
| `get_user_profile` | 获取用户公开资料 |
| `get_recent_ac_submissions` | 获取最近 AC 提交 |
| `get_user_contest_ranking` | 获取竞赛排名 |

### 无认证工具（站点特定）

| 工具 | CN | Global | 说明 |
|------|:--:|:------:|------|
| `get_recent_submissions` | ❌ | ✅ | 最近提交（含失败） |
| `list_problem_solutions` | ✅ | ✅ | 题解列表（参数不同） |
| `get_problem_solution` | ✅ | ✅ | 题解详情（slug vs topicId） |

### 认证工具

| 工具 | CN | Global | 说明 |
|------|:--:|:------:|------|
| `get_user_status` | ✅ | ✅ | 检查登录态 |
| `get_problem_submission_report` | ✅ | ✅ | 提交详情 |
| `get_problem_progress` | ✅ | ✅ | 做题进度 |
| `get_all_submissions` | ✅ | ✅ | 全部提交（CN 支持 lang/status 过滤） |
| `run_code` | ✅ | ✅ | 运行代码 |
| `submit_solution` | ✅ | ✅ | 提交代码 |
| `search_notes` | ✅ | ❌ | 搜索笔记 |
| `get_note` | ✅ | ❌ | 获取笔记 |
| `create_note` | ✅ | ❌ | 创建笔记 |
| `update_note` | ✅ | ❌ | 更新笔记 |

### MCP 资源

| 资源 | URI | 说明 |
|------|-----|------|
| `problem-categories` | `categories://problems/all` | 题目分类 |
| `problem-tags` | `tags://problems/all` | 算法标签 |
| `problem-langs` | `langs://problems/all` | 编程语言 |
| `problem-detail` | `problem://{titleSlug}` | 题目详情 |
| `problem-solution` | `solution://{slug\|topicId}` | 题解内容 |

## 5. 错误处理

### 5.1 异常类型

```python
LeetCodeError          # 基类
├── AuthenticationError  # 认证失败
├── NotFoundError        # 资源不存在
├── RateLimitError       # 请求频率限制
├── NetworkError         # 网络错误
├── GraphQLError         # GraphQL 查询错误
└── SubmissionError      # 代码提交错误
```

### 5.2 工具层错误处理

所有工具 catch 异常后序列化为 JSON 返回，不抛给 MCP 传输层：

```json
{"error": "Failed to run code", "message": "..."}
```

## 6. CN 站 GraphQL 查询差异

| 功能 | CN 查询 | Global 查询 |
|------|---------|-------------|
| 每日一题 | `todayRecord` | `activeDailyCodingChallengeQuestion` |
| 用户资料 | `userProfilePublicProfile(userSlug:)` | `matchedUser(username:)` |
| 搜索题目 | `problemsetQuestionList` | `questionList` (用 alias 映射) |
| 题解列表 | `questionSolutionArticles` | `ugcArticleSolutionArticles` |
| 题解详情 | `solutionArticle(slug:)` | `ugcArticleSolutionArticle(topicId:)` |

## 7. 安全注意事项

- **Session/Cookie**：通过环境变量传入，不硬编码到源码
- **config.yaml**：已在 `.gitignore` 中，不会被提交
- **opencode 配置**：`~/.config/opencode/opencode.json` 在用户目录，不在项目仓库中

## 8. 开发进度

### Phase 1: 基础框架 ✅
- [x] 项目结构
- [x] 配置管理 (config.py)
- [x] HTTP 客户端 (client.py)
- [x] 异常类 (exceptions.py)
- [x] 常量定义 (constants.py)
- [x] 缓存层 (cache.py)

### Phase 2: 核心功能 ✅
- [x] Pydantic 数据模型 (models.py)
- [x] GraphQL 查询 (graphql/cn/ + graphql/lc_global/)
- [x] 服务层 (base_service + cn_service + global_service + factory)
- [x] 问题工具 (problem_tools)
- [x] 用户工具 (user_tools)
- [x] 题解工具 (solution_tools)

### Phase 3: 高级功能 ✅
- [x] 代码执行 (submission_tools: run_code, submit_solution)
- [x] 笔记管理 (note_tools: CN only)
- [x] MCP 资源 (problem_resources + solution_resources)

### Phase 4: 测试与集成 ✅
- [x] 真实 API 端到端验证 (LeetCode CN)
- [x] 18 个工具注册验证
- [x] opencode 集成配置

### 待完善
- [ ] 单元测试
- [ ] Global 端到端验证
- [ ] Streamable HTTP 传输模式
