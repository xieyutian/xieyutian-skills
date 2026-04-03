# GitCode PR Comment 脚本说明

本文档详细说明技能中使用的所有 Python 脚本的参数和用法。

## 脚本列表

| 脚本 | 功能 | 主要用途 |
|------|------|----------|
| `repo_cache.py` | 仓库缓存管理 | 步骤 0：获取/克隆仓库 |
| `get_pr_info.py` | PR 信息获取 | 步骤 2：获取 PR 基本信息 |
| `get_pr_comments.py` | PR 评论获取 | 步骤 3：获取评论列表 |
| `post_comment_reply.py` | 评论回复发布 | 步骤 8：回复评论 |

---

## repo_cache.py

管理仓库 URL 与本地目录的对应关系缓存。

**缓存位置**: `skills/gitcode-pr-comment/memory/repo_cache.json`

**默认克隆目录**: `~/gitcode_repos/<owner>_<repo>/`

### 命令参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--get URL` | 获取仓库路径（缓存不存在则自动克隆） | `--get "https://gitcode.com/owner/repo.git"` |
| `--clone URL` | 只克隆仓库（不检查缓存） | `--clone "https://gitcode.com/owner/repo.git"` |
| `--read URL` | 读取指定仓库的缓存 | `--read "https://gitcode.com/owner/repo.git"` |
| `--write URL PATH` | 写入仓库缓存 | `--write URL PATH` |
| `--owner` | 仓库所有者（配合 --get/--clone） | `--owner <owner>` |
| `--repo` | 仓库名称（配合 --get/--clone） | `--repo <repo>` |
| `--validate PATH` | 验证路径有效性 | `--validate "/path/to/repo"` |
| `--delete URL` | 删除指定仓库缓存 | `--delete URL` |
| `--clean` | 清理所有无效缓存 | `--clean` |
| `--list` | 列出所有缓存 | `--list` |

### 使用示例

```bash
# 获取或克隆仓库（推荐：自动处理缓存和克隆）
python scripts/repo_cache.py --get "https://gitcode.com/<owner>/<repo>.git" --owner <owner> --repo <repo>

# 输出：
{
  "local_path": "/path/to/gitcode_repos/<owner>_<repo>",
  "is_new_clone": true,
  "repo_url": "https://gitcode.com/<owner>/<repo>.git"
}

# 只克隆仓库
python scripts/repo_cache.py --clone "https://gitcode.com/owner/repo.git" --owner owner --repo repo

# 手动写入缓存（使用已有的本地路径）
python scripts/repo_cache.py --write "https://gitcode.com/owner/repo.git" "/path/to/repo" --owner owner --repo repo

# 验证路径有效性
python scripts/repo_cache.py --validate "/path/to/repo"

# 清理无效缓存
python scripts/repo_cache.py --clean

# 列出所有缓存
python scripts/repo_cache.py --list
```

---

## get_pr_info.py

获取指定 Pull Request 的详细信息和审查上下文。

### 命令参数

| 参数 | 说明 | 必填 |
|------|------|------|
| `token` | GitCode access_token | 是 |
| `owner` | 仓库所有者 | 是 |
| `repo` | 仓库名称 | 是 |
| `pr_number` | PR 编号 | 是 |
| `--review-context` | 输出完整审查上下文（默认） | 否 |
| `--files` | 只输出文件变更列表 | 否 |
| `--commits` | 只输出 commits 信息 | 否 |
| `--show-patch` | 显示文件 patch 预览 | 否 |
| `--json` | 输出 JSON 格式 | 否 |

### 环境变量支持

- `GITCODE_TOKEN` 或 `GITCODE_ACCESS_TOKEN`: Token
- `REPO_OWNER`: 仓库所有者
- `REPO_NAME`: 仓库名称
- `PR_NUMBER`: PR 编号

### 使用示例

```bash
# 获取完整审查上下文（默认）
python scripts/get_pr_info.py <token> <owner> <repo> <pr_number>

# 只获取文件变更列表
python scripts/get_pr_info.py <token> <owner> <repo> <pr_number> --files

# 输出 JSON 格式
python scripts/get_pr_info.py <token> <owner> <repo> <pr_number> --json

# 输出示例：
{
  "pr_number": 123,
  "title": "Add new feature",
  "author": "<pr_author>",
  "state": "open",
  "description": "...",
  "modification_points": ["新增功能A", "修复问题B"],
  "files": [
    {"filename": "src/main.cj", "status": "added", "additions": 50, "deletions": 0}
  ],
  "commits": [
    {"sha": "abc123", "message": "feat: add new feature", "author": "<author>"}
  ]
}
```

---

## get_pr_comments.py

获取指定 Pull Request 的所有评论信息。

### 命令参数

| 参数 | 说明 | 必填 |
|------|------|------|
| `token` | GitCode access_token | 是 |
| `owner` | 仓库所有者 | 是 |
| `repo` | 仓库名称 | 是 |
| `pr_number` | PR 编号 | 是 |
| `--type` | 评论类型筛选：`diff_comment`(代码行) / `pr_comment`(整体) | 否 |
| `--json` | 输出 JSON 格式 | 否 |
| `--analysis` | 输出分析上下文（推荐） | 否 |

### 使用示例

```bash
# 获取所有评论（分析上下文格式，推荐）
python scripts/get_pr_comments.py <token> <owner> <repo> <pr_number> --analysis

# 只获取代码行评论
python scripts/get_pr_comments.py <token> <owner> <repo> <pr_number> --type diff_comment

# 输出 JSON 格式
python scripts/get_pr_comments.py <token> <owner> <repo> <pr_number> --json

# 输出示例：
{
  "total_comments": 5,
  "diff_comments": [
    {
      "id": 123456789,
      "discussion_id": "abc123def456...",
      "body": "这里存在安全风险",
      "user": "<reviewer>",
      "path": "src/main.cj",
      "position": 10,
      "created_at": "2026-03-31T10:00:00Z"
    }
  ],
  "pr_comments": [...]
}
```

### 关键字段说明

| 字段 | 说明 | 用途 |
|------|------|------|
| `id` | 评论 ID（数字） | 引用评论 |
| `discussion_id` | 讨论 ID（长字符串） | **线程式回复（重要）** |
| `path` | 文件路径 | 定位问题代码 |
| `position` | 行号 | 定位问题代码 |
| `diff_position` | 详细行号信息 | 精确定位 |

> **重要**: 回复评论使用 `discussion_id`，不是 `comment_id`！

---

## post_comment_reply.py

在修复问题后回复评论说明已修复。

### 命令参数

| 参数 | 说明 | 必填 |
|------|------|------|
| `token` | GitCode access_token | 是 |
| `owner` | 仓库所有者 | 是 |
| `repo` | 仓库名称 | 是 |
| `pr_number` | PR 编号 | 是 |
| `--detailed-replies` | 详细回复映射（JSON格式） | 否 |
| `--discussion-id` | 讨论 ID（线程式回复） | 否 |
| `--message` | 评论/回复内容 | 否 |
| `--summary` | 发布修复总结评论 | 否 |
| `--commit-sha` | 修复提交 SHA | 配合 --summary |
| `--fixed-issues` | 已修复问题列表（逗号分隔） | 配合 --summary |
| `--fixed-issue-ids` | 已修复评论 ID 列表（逗号分隔） | 否 |
| `--path` | 文件路径（行级评论） | 否 |
| `--position` | 行号（行级评论） | 否 |

### 使用示例

```bash
# 详细回复每个评论（推荐：使用 discussion_id，回复显示在原评论下方）
python scripts/post_comment_reply.py <token> <owner> <repo> <pr_number> \
  --detailed-replies '{"<discussion_id_1>": "修复说明1", "<discussion_id_2>": "修复说明2"}'

# 使用 discussion_id 回复单个评论
python scripts/post_comment_reply.py <token> <owner> <repo> <pr_number> \
  --discussion-id "<discussion_id>" --message "已修复"

# 发布修复总结
python scripts/post_comment_reply.py <token> <owner> <repo> <pr_number> \
  --summary --commit-sha <commit_sha> --fixed-issues "问题1,问题2"

# 发布单条评论
python scripts/post_comment_reply.py <token> <owner> <repo> <pr_number> \
  --message "感谢审查！"
```

### discussion_id vs comment_id

| 字段 | 格式 | 示例 | 用途 |
|------|------|------|------|
| `discussion_id` | 长字符串 | `abc123def456...` | **线程式回复（推荐）** |
| `comment_id` | 数字 | `123456789` | 简单回复（已弃用） |

> 使用 `discussion_id` 回复会显示在原评论下方（线程式），便于追踪。

---

## 环境变量速查

所有脚本支持以下环境变量：

```bash
# Token
export GITCODE_TOKEN="<your-token>"
export GITCODE_ACCESS_TOKEN="<your-token>"  # 别名

# 仓库信息
export REPO_OWNER="<owner>"
export REPO_NAME="<repo>"
export PR_NUMBER="<pr_number>"
```

设置环境变量后，可以简化命令：

```bash
# 无需传递位置参数
python scripts/get_pr_info.py
python scripts/get_pr_comments.py --analysis
python scripts/post_comment_reply.py --summary --commit-sha abc123
```