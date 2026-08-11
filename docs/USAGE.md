# MCP LeetCode 使用指南

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/LYCGGG/mcp-leetcode.git
cd mcp-leetcode

# 安装依赖
pip install -e .
```

### 2. 获取 LeetCode Cookie

1. 登录 [leetcode.cn](https://leetcode.cn) 或 [leetcode.com](https://leetcode.com)
2. 打开浏览器开发者工具 (F12)
3. 切换到 Application/存储 标签
4. 找到 Cookie，复制以下两个值：
   - `LEETCODE_SESSION`
   - `csrftoken`

### 3. 配置

#### 方式一：环境变量

```bash
# Windows PowerShell
$env:LEETCODE_SITE="cn"
$env:LEETCODE_SESSION="你的session值"
$env:LEETCODE_CSRF="你的csrf值"

# Linux/Mac
export LEETCODE_SITE=cn
export LEETCODE_SESSION="你的session值"
export LEETCODE_CSRF="你的csrf值"
```

#### 方式二：配置文件

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml`：

```yaml
site: cn
auth:
  session: "你的session值"
  csrf_token: "你的csrf值"
cache:
  enabled: true
  ttl_seconds: 300
logging:
  level: INFO
```

#### 方式三：MCP 客户端配置

**opencode** (`.opencode/mcp.json`):

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

**Claude Desktop** (`claude_desktop_config.json`):

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

## 可用工具

### 问题相关

| 工具 | 说明 | 参数 |
|------|------|------|
| `get_daily_challenge` | 获取每日一题 | 无 |
| `get_problem` | 获取题目详情 | `title_slug` |
| `search_problems` | 搜索题目 | `tags`, `difficulty`, `limit` |

### 用户相关

| 工具 | 说明 | 参数 |
|------|------|------|
| `get_user_profile` | 获取用户信息 | `username` |
| `get_recent_ac_submissions` | 获取最近通过的提交 | `username`, `limit` |
| `get_user_contest_ranking` | 获取竞赛排名 | `username` |

### 题解相关

| 工具 | 说明 | 参数 |
|------|------|------|
| `list_problem_solutions` | 获取题解列表 | `question_slug`, `limit` |
| `get_problem_solution` | 获取题解详情 | `identifier` |

### 代码执行 (需要认证)

| 工具 | 说明 | 参数 |
|------|------|------|
| `run_code` | 运行代码 | `title_slug`, `lang`, `typed_code` |
| `submit_solution` | 提交代码 | `title_slug`, `lang`, `typed_code` |

### 笔记管理 (CN only，需要认证)

| 工具 | 说明 | 参数 |
|------|------|------|
| `get_notes` | 获取笔记 | `question_id` |
| `create_note` | 创建笔记 | `question_id`, `content` |
| `update_note` | 更新笔记 | `note_id`, `content` |

## 使用示例

### 获取每日一题

```
调用 get_daily_challenge
返回今日的题目信息
```

### 搜索题目

```
调用 search_problems
参数: tags=["array", "dynamic-programming"], difficulty="MEDIUM", limit=10
返回符合条件的题目列表
```

### 运行代码

```
调用 run_code
参数:
  title_slug: "two-sum"
  lang: "python3"
  typed_code: "def twoSum(nums, target):\n    ..."
返回执行结果
```

## 故障排除

### 认证失败

- 检查 Cookie 是否过期
- 确认 `LEETCODE_SESSION` 和 `csrf_token` 正确
- 确认站点配置正确 (cn/global)

### 连接失败

- 检查网络连接
- 确认 LeetCode API 可访问

### 工具未加载

- 检查 MCP 客户端配置
- 确认 `python -m leetcode_mcp.server` 可以正常运行
