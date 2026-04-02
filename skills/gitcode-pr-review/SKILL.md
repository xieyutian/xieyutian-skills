---
name: gitcode-pr-review
description: GitCode 平台 Pull Request 自动化代码审查技能。当用户提供 GitCode PR URL 或提到"审查 GitCode PR"、"GitCode 代码评审"时触发。支持自动获取 PR 信息、执行安全/质量审查、发布行级评论到 GitCode。必须提供 GitCode Token。
---

# GitCode PR Review

对 GitCode 平台的 Pull Request 进行自动化代码审查，识别潜在问题、安全漏洞并提供改进建议。

## 使用前提

- 系统已安装 Git 和 Python3（含 requests 库）
- 已配置 GitCode Token（用于发布评论）

## 输入参数

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| 仓库 Clone 地址 | GitCode 仓库克隆地址 | 是* | `https://gitcode.com/user/repo.git` |
| PR 编号 | Pull Request 编号 | 是 | `123` |
| GitCode Token | 个人访问令牌 | 是 | `your-token` |
| 本地仓库路径 | 已有的仓库目录 | 否* | `/home/user/myproject` |

> *注：如提供本地仓库路径，Clone 地址可从本地获取。

## 流程变量

执行中需记录以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `REPO_DIR` | 仓库绝对路径 | `/home/user/pr_review/myproject` |
| `HAS_LOCAL_REPO` | 是否使用已有仓库 | `true` / `false` |
| `ORIGINAL_BRANCH` | 原始分支名 | `main` |
| `HAS_STASH` | 是否执行了 stash | `true` / `false` |

> **重要**：`REPO_DIR` 最关键，后续 git 命令都必须使用 `git -C "$REPO_DIR"` 语法。

## 缓存机制

缓存文件：`~/.gitcode-pr-review/repo_cache.json`

格式：`{"repos": {"<仓库URL>": "<本地路径>"}}`

用途：下次审查相同仓库时自动使用缓存路径，无需重复询问。

---

## 审查流程

### 步骤 0: 确认工作环境

**首先检查缓存**：
1. 从 PR URL 提取仓库 URL
2. 读取缓存文件，检查是否有匹配路径
3. 验证路径有效性：有效则自动使用，无效则清理缓存

**缓存未命中时询问**：用户是否有仓库目录？

---

**情况 A：用户已有仓库**

1. 记录仓库绝对路径：`pwd` → `REPO_DIR`
2. 记录原始分支：`git -C "$REPO_DIR" branch --show-current`
3. 检查工作区状态，如有未提交修改则 stash
4. 继续步骤 2

---

**情况 B：用户没有仓库**

执行步骤 1 克隆仓库，然后继续步骤 2。

---

### 步骤 1: 克隆仓库

```bash
mkdir -p pr_review && cd pr_review && git clone <仓库地址> && pwd
```

**立即记录**：`REPO_DIR = <pwd输出>/<项目名>`

### 步骤 2: 获取 PR 分支

```bash
git -C "$REPO_DIR" fetch <仓库地址> merge-requests/<PR编号>/head:review-<PR编号>
git -C "$REPO_DIR" checkout review-<PR编号>
```

### 步骤 3: 验证变更范围（关键！）

> **常见错误**：`git diff origin/dev review-<PR>` 会显示所有累积差异，而非 PR 实际变更。

**正确方法**（三选一）：

```bash
# 方法 1：通过 API（推荐）
python3 <技能目录>/scripts/get_pr_info.py <Token> <owner> <repo> <PR编号> --files

# 方法 2：merge-base
git -C "$REPO_DIR" diff $(git -C "$REPO_DIR" merge-base origin/dev review-<PR编号>) review-<PR编号> --stat

# 方法 3：查看 commits
git -C "$REPO_DIR" log origin/dev..review-<PR编号> --oneline
```

### 步骤 4: 获取审查上下文

```bash
python3 <技能目录>/scripts/get_pr_info.py <Token> <owner> <repo> <PR编号>
```

输出包含：PR 基本信息、声称的修改点、文件变更、commits 信息。

**关键用途**：理解 PR 目的，验证修改是否全面覆盖声称的问题。

### 步骤 5: 执行代码审查

> **重要**：基于**完整文件内容**审查，而非仅看 diff。

**审查步骤**：
1. 获取变更文件列表（API）
2. 使用 Read 工具读取完整文件
3. 查看 diff 了解具体修改
4. **逐项执行审查清单**（见 `references/checklists.md`）
5. 综合分析输出报告

**详细审查清单**请参阅：[checklists.md](references/checklists.md)

### 步骤 6: 展示报告并确认发布

**先展示完整报告**，然后询问是否发布到 GitCode PR。

**用户确认后执行**：

```bash
export GITCODE_TOKEN="<Token>"
export REPO_OWNER="<owner>"
export REPO_NAME="<repo>"
export PR_NUMBER="<PR编号>"

python3 <技能目录>/scripts/pr-comment.py -f <技能目录>/pr_review_report.md --parse-report
```

**行级评论格式规范**请参阅：[comment-format.md](references/comment-format.md)

### 步骤 7: 清理和恢复

**情况 B（新克隆仓库）**：询问是否删除临时目录

**情况 A（用户已有仓库）**：
1. 切换回原分支：`git -C "$REPO_DIR" checkout <ORIGINAL_BRANCH>`
2. 恢复 stash（如有）：`git -C "$REPO_DIR" stash pop`
3. 确认恢复成功

---

## 审查报告格式

报告必须包含以下章节：

1. PR 描述分析 - 验证声称的修改点
2. 修改全面性评估 - 检查遗漏项
3. 变更概述 - 简要描述变更
4. 优点 - 值得肯定的方面
5. 潜在问题 - 必须包含文件路径和行号
6. 改进建议 - 推荐的改进项
7. 总体评价 - 多维度评分

**详细格式规范**：[report-template.md](references/report-template.md)

**行级评论格式**：[comment-format.md](references/comment-format.md)

---

## 注意事项

- **必须首先询问本地仓库**，避免重复克隆
- **必须记录 REPO_DIR**：后续命令使用 `git -C "$REPO_DIR"`
- **必须保护工作区**：有未提交修改时自动 stash
- **必须基于完整文件审查**，而非仅看 diff
- **必须执行审查清单**：逐项检查，不得遗漏
- **行级评论只能引用实际代码**：严禁虚构代码片段
- **行号支持范围格式**：`#L10` 或 `#L10-15`（脚本自动取首行号）
- **必须验证变更范围**：使用 API 或 merge-base，避免累积差异

---

## 参考文件

| 文件 | 用途 |
|------|------|
| [checklists.md](references/checklists.md) | 完整审查清单 |
| [comment-format.md](references/comment-format.md) | 行级评论格式规范 |
| [report-template.md](references/report-template.md) | 报告格式模板 |
| [examples.md](references/examples.md) | 完整执行示例 |