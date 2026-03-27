---
name: gitcode-pr-review
description: GitCode Pull Request 自动批量审查技能。自动扫描 Cangjie 组织的两个核心仓库（runtime、stdx）最新开启的 PR，跳过已审查的，对未审查的 PR 执行深度代码审查并发表评论。
---

# GitCode PR Review（批量自动审查版）

自动扫描 GitCode 平台上 Cangjie 组织的两个核心仓库，批量审查最新开启的 Pull Request，跳过已审查的，对未审查的 PR 执行深度代码审查、识别潜在问题、安全漏洞并提供改进建议。

## 固定审查范围

本技能**自动审查**以下两个仓库，无需用户提供仓库地址：

| 仓库 | Clone 地址 | 说明 |
|------|------------|------|
| cangjie_runtime | `https://gitcode.com/Cangjie/cangjie_runtime.git` | 运行时仓库 |
| cangjie_stdx | `https://gitcode.com/Cangjie/cangjie_stdx.git` | 标准库扩展仓库 |

**审查策略**：每个仓库获取最新开启的 **10 个 open 状态 PR**，自动跳过已审查的 PR。

### 目录筛选规则（cangjie_runtime 仓库专属）

> **重要**：对于 `cangjie_runtime` 仓库，仅审查修改 `stdlib` 目录的 PR，跳过修改 `runtime` 目录的 PR。

| 筛选条件 | 处理方式 | 说明 |
|----------|----------|------|
| 仅修改 `stdlib/` 及其子目录 | **执行审查** | 标准库相关变更 |
| 修改了 `runtime/` 及其子目录 | **跳过审查** | 运行时底层实现，不审查 |
| 同时修改 `stdlib/` 和 `runtime/` | **跳过审查** | 混合变更，暂不审查 |

**筛选方法**：通过 GitCode API 获取 PR 的变更文件列表，检查文件路径前缀：
- 文件路径以 `stdlib/` 开头 → 符合审查条件
- 文件路径以 `runtime/` 开头 → 跳过此 PR

## 使用前提

- 系统已安装 Git
- 系统已安装 Python3 和 requests 库
- 有足够的磁盘空间克隆仓库
- **已配置 GitCode Token**（用于自动获取PR列表、检查审查状态、发布评论）

## 输入参数

执行审查前需获取以下信息：

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| GitCode Token | GitCode 个人访问令牌（用于获取PR列表、检查审查状态、发布评论） | 是 | `your-token` |
| 本地仓库路径 | 用户已有的仓库目录路径（可选，用于覆盖缓存） | 否 | `/home/user/cangjie_runtime` |

> **重要变更**：仓库地址和 PR 编号**不再需要用户提供**，由技能自动从固定两个仓库获取最新 PR。

## 流程变量

执行过程中需记录以下变量，用于后续恢复：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `REPO_DIR` | 仓库的绝对路径 | `/home/user/pr_review/myproject` |
| `HAS_LOCAL_REPO` | 是否使用用户已有仓库 | `true` / `false` |
| `ORIGINAL_BRANCH` | 用户原始分支名 | `main` / `dev` |
| `ORIGINAL_DIR` | 用户原始工作目录 | `/home/user/myproject` |
| `HAS_STASH` | 是否执行了 stash | `true` / `false` |

> **重要**：`REPO_DIR` 是最关键的变量，所有后续 git 命令都必须使用此路径，避免 Bash 会话隔离导致的路径丢失问题。

## 缓存机制

技能会自动记录仓库与本地目录的对应关系，存储在项目的 memory 目录中。

**缓存文件**：`~/.gitcode-pr-review/repo_cache.json`

**缓存格式**：
```json
{
  "repos": {
    "<仓库Clone地址>": "<本地目录路径>"
  }
}
```

**用途**：下次审查相同仓库的 PR 时，自动使用缓存的本地目录，无需重复询问。

**首次使用**：缓存文件不存在时会自动创建，无需手动配置。

**缓存失效处理**：自动检测目录是否存在，不存在时清理缓存并重新询问用户。

## 审查流程（批量自动模式）

### 步骤 0: 准备工作（必须首先执行）

**0.1 获取 GitCode Token**

如果用户未提供 Token，询问获取：
> 请提供 GitCode 个人访问令牌（Token）。
> 获取方式：https://gitcode.com/-/profile/personal_access_tokens

**0.2 获取当前用户名**

执行命令获取当前认证用户：

```bash
# 使用 action 模式（推荐）
python3 <技能目录>/scripts/get_pr_info.py --token <GitCode Token> --action get_user

# Windows 用户将 python3 替换为 python
```

输出示例：
```json
{
  "login": "your_username",
  "id": 12345,
  "name": "Your Name",
  "email": "your@email.com"
}
```

**记录变量**：`CURRENT_USER = <login 字段值>`

---

### 步骤 1: 批量扫描 PR

遍历两个固定仓库，获取每个仓库的最新 open PR：

**仓库列表**：
1. `Cangjie/cangjie_runtime`
2. `Cangjie/cangjie_stdx`

**对每个仓库执行**：

```bash
# 获取最新 10 个 open PR（使用 action 模式）
python3 <技能目录>/scripts/get_pr_info.py --token <GitCode Token> --owner Cangjie --repo <repo_name> --action list_prs --per-page 10

# Windows 用户将 python3 替换为 python
```

输出示例：
```json
[
  {
    "number": 1028,
    "title": "修复运行时类型推断问题",
    "user": "developer1",
    "created_at": "2025-03-28T10:00:00Z",
    "head_branch": "fix-type-inference",
    "base_branch": "main",
    "html_url": "https://gitcode.com/Cangjie/cangjie_runtime/pulls/1028"
  },
  ...
]
```

> **参数说明**：
> - `--per-page`：每页返回的 PR 数量，默认 10，最大 100

---

### 步骤 2: 检查审查状态

对每个获取到的 PR，检查当前用户是否已发表过评论：

```bash
# 检查是否已审查（使用 action 模式）
python3 <技能目录>/scripts/get_pr_info.py --token <GitCode Token> --owner Cangjie --repo <repo_name> --pr <pr_number> --username <CURRENT_USER> --action check_reviewed

# Windows 用户将 python3 替换为 python
```

> **参数说明**：
> - `--username`：要检查的用户名，如果不提供会自动获取当前用户

输出示例：
```json
{
  "pr_number": 1028,
  "username": "your_username",
  "already_reviewed": false
}
```

**处理逻辑**：
- `already_reviewed: true` → **跳过此 PR**，输出「⏭️ 已跳过 PR #1028（已审查）」
- `already_reviewed: false` → **执行目录筛选检查**

---

### 步骤 2.5: 目录筛选检查（仅 cangjie_runtime 仓库）

> **目的**：对于 cangjie_runtime 仓库，检查 PR 的变更文件是否在 stdlib 目录下。

**执行命令**（获取变更文件列表）：

```bash
python3 <技能目录>/scripts/get_pr_info.py --token <GitCode Token> --owner Cangjie --repo cangjie_runtime --pr <pr_number> --files

# Windows 用户将 python3 替换为 python
```

**筛选逻辑**：

1. 解析返回的文件列表，提取每个文件的路径
2. 检查文件路径前缀：
   - 如果**所有**变更文件路径都以 `stdlib/` 开头 → **执行审查**
   - 如果**任意**变更文件路径以 `runtime/` 开头 → **跳过此 PR**
3. 输出筛选结果：
   - 符合条件：`✅ PR #1028 符合审查条件（仅修改 stdlib 目录）`
   - 不符合条件：`⏭️ 已跳过 PR #1028（修改了 runtime 目录）`

**示例**：

```
=== PR #1059 文件变更 ===
  [?] stdlib/libs/std/core/thread.cj (+11/-8)
  [?] stdlib/libs/std/core/c_pointer_resource.cj (+4/-6)
  [?] stdlib/libs/std/core/c_string_resource.cj (+4/-6)
✅ PR #1059 符合审查条件（仅修改 stdlib 目录）

=== PR #1056 文件变更 ===
  [?] runtime/CMakeLists.txt (+12/-17)
  [?] runtime/build/windows_rename_section.sh (+0/-47)
  [?] runtime/src/StackManager.cpp (+1/-1)
⏭️ 已跳过 PR #1056（修改了 runtime 目录）
```

> **注意**：此筛选仅适用于 `cangjie_runtime` 仓库，`cangjie_stdx` 仓库无需筛选。

---

### 步骤 3: 单 PR 审查子流程（复用原有流程）

对每个需要审查的 PR，执行以下子流程（对应原有的「步骤 0-7」）：

#### 3.0 确认工作环境

**检查缓存**：
1. 读取缓存文件 `~/.gitcode-pr-review/repo_cache.json`
2. 检查是否存在该仓库（如 `https://gitcode.com/Cangjie/cangjie_runtime.git`）的本地路径
3. 如果缓存有效：自动使用，跳过询问
4. 如果缓存无效或不存在：询问用户是否有本地仓库目录

**询问流程**（仅当缓存未命中时）：
> 请问您是否已有 `Cangjie/<repo_name>` 仓库的本地克隆目录？
> - 如果有，请提供目录路径
> - 如果没有，我将为您克隆仓库

**情况 A：用户已有仓库目录**
- 记录 `REPO_DIR`、`ORIGINAL_BRANCH`
- 检查工作区状态，如有未提交修改则 stash

**情况 B：用户没有仓库目录**
- 执行克隆：`mkdir -p pr_review && cd pr_review && git clone https://gitcode.com/Cangjie/<repo_name>.git`
- 记录 `REPO_DIR = <pwd>/<repo_name>`

#### 3.1-3.4 获取并切换 PR 分支

```bash
# 获取 PR 分支
git -C "$REPO_DIR" fetch https://gitcode.com/Cangjie/<repo_name>.git merge-requests/<PR编号>/head:review-<PR编号>

# 切换分支
git -C "$REPO_DIR" checkout review-<PR编号>
```

#### 3.5 获取 PR 审查上下文

```bash
# 传统模式（位置参数）
python3 <技能目录>/scripts/get_pr_info.py <GitCode Token> Cangjie <repo_name> <PR编号>

# 或使用命名参数模式
python3 <技能目录>/scripts/get_pr_info.py --token <GitCode Token> --owner Cangjie --repo <repo_name> --pr <PR编号>

# Windows 用户将 python3 替换为 python
```

#### 3.6 执行代码审查

按照原有「步骤 5」执行：
1. 获取变更文件列表
2. 读取完整文件内容（使用 Read 工具）
3. 查看 diff 了解具体修改
4. 执行修改全面性和正确性审查清单
5. 执行安全审查清单
6. 执行代码质量审查清单
7. 综合分析并输出报告

#### 3.7 自动发布审查报告

审查完成后，**自动将审查报告发布到 GitCode PR**，无需用户确认（适合自动化场景）：

> ✅ 审查报告已自动发布到 GitCode PR #<PR编号>

**发布评论命令**：

```bash
export GITCODE_TOKEN="<GitCode Token>"
export REPO_OWNER="Cangjie"
export REPO_NAME="<repo_name>"
export PR_NUMBER="<PR编号>"

python3 <技能目录>/scripts/pr-comment.py -f <技能目录>/pr_review_report.md --parse-report
```

#### 3.8 清理和恢复

**情况 A（用户已有仓库）**：
```bash
git -C "$REPO_DIR" checkout <ORIGINAL_BRANCH>
git -C "$REPO_DIR" stash pop  # 如果之前有 stash
```

**情况 B（新克隆仓库）**：
询问是否清理临时目录，如用户同意则 `rm -rf "$(dirname "$REPO_DIR")"`

---

### 步骤 4: 继续下一个 PR

完成当前 PR 审查后，返回「步骤 2」处理下一个 PR。

---

### 步骤 5: 输出汇总

全部 PR 处理完成后，输出汇总报告：

```
📊 批量审查完成汇总

仓库：Cangjie/cangjie_runtime
  - 扫描 PR：10 个
  - 已跳过（已审查）：X 个
  - 已审查发布：X 个
  - 跳过发布：X 个

仓库：Cangjie/cangjie_stdx
  ...

总计：
  - 扫描 PR：20 个
  - 已跳过（已审查）：X 个
  - 新审查发布：X 个
  - 跳过发布：X 个
```


### 步骤 4.3: 验证 PR 实际变更范围（关键！）

> **重要**：必须验证 PR 的实际变更范围，避免看到所有累积差异！

**常见错误**：
```bash
# ❌ 错误：这会显示两个分支之间的所有累积差异
git -C "$REPO_DIR" diff origin/dev review-<PR 编号> --stat
# 可能显示 925 个文件变更（实际 PR 只有 3 个文件）
```

**正确方法**（三选一）：

**方法 1：通过 GitCode API 获取（推荐）**
```bash
# 传统模式
python3 <技能目录>/scripts/get_pr_info.py <Token> <owner> <repo> <PR 编号> --files

# 或使用命名参数模式
python3 <技能目录>/scripts/get_pr_info.py --token <Token> --owner <owner> --repo <repo> --pr <PR 编号> --files

# Windows 用户将 python3 替换为 python
```

**方法 2：使用 merge-base 计算正确的 diff 范围**
```bash
git -C "$REPO_DIR" diff $(git -C "$REPO_DIR" merge-base origin/dev review-<PR 编号>) review-<PR 编号> --stat
```

**方法 3：查看 PR 的实际 commits**
```bash
git -C "$REPO_DIR" log origin/dev..review-<PR 编号> --oneline
```

**验证步骤**：
1. 通过 API 获取变更文件数
2. 使用 `git diff --stat` 验证
3. 如果不一致，**以 API 为准**

**原因说明**：
- PR 分支可能从目标分支的**旧版本**创建
- 之后目标分支有其他 PR 的提交
- 直接 `git diff origin/dev review-<PR>` 会显示**所有累积差异**
- 使用 `merge-base` 可以找到共同祖先，只显示 PR 的实际变更

### 步骤 4.5: 获取 PR 审查上下文（重要）

> **目的**：通过 API 获取 PR 的详细信息和文件变更，用于评估修改的全面性和正确性。

**执行命令**：

```bash
# 从 Clone 地址提取 owner 和 repo
# 例如 https://gitcode.com/Cangjie/cangjie_runtime.git -> owner=Cangjie, repo=cangjie_runtime

# 传统模式（位置参数）
python3 <技能目录>/scripts/get_pr_info.py <GitCode Token> <owner> <repo> <PR编号>

# 或使用命名参数模式
python3 <技能目录>/scripts/get_pr_info.py --token <GitCode Token> --owner <owner> --repo <repo> --pr <PR编号>

# Windows 用户将 python3 替换为 python
```

> **跨平台提示**：Windows 用户将 `python3` 替换为 `python`

**输出内容**：

脚本会输出以下审查上下文信息：
- PR 基本信息（标题、作者、状态、源/目标分支）
- **声称的修改点**（从 PR 描述中提取）
- 文件变更统计和列表
- Commits 信息
- 结构化数据（供 AI 审查使用）

**关键用途**：
1. 理解 PR 的修改目的和声称解决的问题
2. 用于后续验证修改是否全面覆盖声称的问题
3. 用于验证修改逻辑的正确性

### 步骤 5: 执行代码审查

> **重要**：审查应基于**完整文件内容**进行，而不仅仅是 diff 片段。
> 这样可以看到函数完整定义、调用关系、上下文等，确保审查全面。

**审查步骤**：

1. **获取变更文件列表**（通过 API）：

```bash
# 传统模式（位置参数）
python3 <技能目录>/scripts/get_pr_info.py <Token> <owner> <repo> <PR编号> --files

# 或使用命名参数模式
python3 <技能目录>/scripts/get_pr_info.py --token <Token> --owner <owner> --repo <repo> --pr <PR编号> --files

# Windows 用户将 python3 替换为 python
```

> **跨平台提示**：Windows 用户将 `python3` 替换为 `python`

输出示例：
```
文件变更 (3 个文件)
统计:
  新增: 0 | 修改: 3 | 删除: 0
  +150 行, -30 行

文件列表:
  [~] src/main.c (+50/-10)
  [~] src/utils.c (+80/-15)
  [~] src/header.h (+20/-5)
```

2. **查看完整文件内容**（在本地仓库审查分支上）：

```bash
# 使用 Read 工具读取文件（推荐，可以看到行号）
# 文件路径: $REPO_DIR/<文件路径>

# 或使用 git show 查看审查分支上的文件
git -C "$REPO_DIR" show review-<PR编号>:<文件路径>
```

3. **查看 diff 了解具体修改**：

```bash
git -C "$REPO_DIR" diff main...review-<PR编号> --stat
git -C "$REPO_DIR" diff main...review-<PR编号>
```

4. **基于完整文件内容进行深度审查**：

> **关键改进**：不仅看 diff 片段，还要看完整函数/类定义、调用位置、相关代码

| 审查方法 | 命令/操作 | 目的 |
|----------|-----------|------|
| 查看完整函数 | Read 工具读取文件 | 理解函数完整逻辑 |
| 查看调用位置 | `grep -n "函数名" -r "$REPO_DIR"` | 确认修改影响范围 |
| 查看相关类型定义 | Read 工具读取头文件 | 理解数据结构 |
| 对比修改前后 | `git -C "$REPO_DIR" diff main...review-<PR编号>` | 理解具体修改 |

5. **逐项执行修改全面性和正确性审查清单**（必须检查）：

#### 修改全面性和正确性审查清单（强制检查项）

| 检查项 | 检查内容 | 说明 |
|--------|----------|------|
| [!] PR 描述对照 | PR 描述中声称修改的内容是否都已实现 | 修改全面性 |
| [?] 问题定位准确性 | 修复的问题是否是真正的问题 | Bug 修复类 PR |
| [+] 修改完整性 | 是否遗漏相关文件或代码路径 | 跨文件修改 |
| [*] 测试覆盖 | 是否包含必要的测试用例 | 功能开发类 PR |

**审查方法**：
- 对照步骤 4.5 中提取的「声称的修改点」，逐一验证是否在代码中实现
- **读取完整文件内容**，理解函数完整逻辑和上下文
- 检查是否有遗漏的边界情况或错误处理
- 验证修改逻辑是否正确解决了声称的问题

6. **逐项执行安全审查清单**（必须全部检查）：

#### 安全审查清单（强制检查项）

| 检查项 | 检查内容 | 常见问题示例 |
|--------|----------|--------------|
| [K] 硬编码密钥 | 搜索 `key`、`secret`、`password`、`token`、`iv` 等关键词 | `let key = "xxx"`、`password = "123456"` |
| [L] 加密安全 | 检查加密算法、密钥管理、IV 使用 | 弱算法(MD5/DES)、固定IV、密钥硬编码 |
| [I] 输入验证 | 检查用户输入是否经过验证和过滤 | SQL注入、XSS、命令注入风险 |
| [F] 文件操作 | 检查路径拼接、权限控制 | 路径遍历、任意文件读写 |
| [N] 网络请求 | 检查 URL、证书、敏感数据传输 | HTTP 明文传输、证书绕过 |
| [O] 日志输出 | 检查是否记录敏感信息 | 密码、密钥、个人信息写入日志 |
| [P] 权限控制 | 检查权限检查逻辑 | 越权访问、权限绕过 |

**执行方式**：
```bash
# 在本地仓库中检查硬编码密钥
grep -rnE "(key|secret|password|token|iv)\s*=\s*[\"']" "$REPO_DIR"

# 检查敏感关键词
grep -rnE "(encrypt|decrypt|hash|crypto|auth)" "$REPO_DIR/<变更文件路径>"
```

7. **逐项执行代码质量审查清单**（必须全部检查）：

#### 代码质量审查清单（强制检查项）

| 检查项 | 检查内容 | 常见问题示例 |
|--------|----------|--------------|
| [B] 逻辑错误 | 条件判断、循环边界、异常处理 | 边界条件遗漏、空指针、死循环 |
| [E] 性能问题 | 循环效率、内存使用、资源泄漏 | O(n^2) 循环、大对象未释放、连接未关闭 |
| [N] 命名规范 | 变量、函数、类的命名 | 单字母变量、误导性命名、风格不一致 |
| [S] 代码结构 | 函数长度、嵌套深度、模块划分 | 过长函数、深层嵌套、职责不清 |
| [R] 可读性 | 注释、代码格式、逻辑清晰度 | 魔法数字、复杂表达式无注释 |
| [D] 重复代码 | 相似逻辑是否可提取 | 多处重复的代码片段 |
| [H] 错误处理 | 异常捕获、错误传播、降级策略 | 吞掉异常、错误信息丢失 |

**审查方法**：
- **使用 Read 工具读取完整文件**，理解代码上下文
- 对每个变更文件逐行审查，关注函数完整逻辑
- 对照上述检查项逐一确认
- 发现问题时记录文件路径、行号和代码片段

8. **综合分析并输出报告**：
   - 汇总修改全面性、安全审查和代码质量审查的发现
   - 对问题进行风险分级（高/中/低）
   - 提供具体的修复建议

**审查完成后**：按照下方「审查报告格式规范」输出标准化报告。

## 审查报告格式规范

审查报告必须严格按照标准格式输出。**详细格式规范请参阅**: `references/report-template.md`

**简要要求**：
- 必须包含：PR 描述分析、修改全面性评估、变更概述、优点、潜在问题、改进建议、总体评价
- 潜在问题必须包含文件路径和行号，格式为 ` ```语言:文件路径#L行号`` `
- 每个问题必须标注风险等级（高/中/低）
- 全部使用中文输出

### 步骤 6: 自动发布审查报告

审查完成后，**自动将审查报告发布到 GitCode PR**，无需用户确认（适合自动化场景）。

> ✅ 审查报告已自动发布到 GitCode PR #<PR编号>
> - 潜在问题已作为**行级评论**发布到对应的文件和代码行
> - 改进建议已作为**整体评论**发布

**自动执行发布**：

1. 将完整审查报告保存到临时文件（技能目录下的 `pr_review_report.md`）
2. 设置环境变量并执行评论发布脚本（使用 `--parse-report` 参数）

**执行命令**：

```bash
# 设置环境变量
export GITCODE_TOKEN="<GitCode Token>"
export REPO_OWNER="<仓库所有者>"
export REPO_NAME="<仓库名称>"
export PR_NUMBER="<PR编号>"

# 解析审查报告并发布评论（潜在问题作为行级评论，改进建议作为整体评论）
# Windows 用户使用 python，Linux/macOS 用户使用 python3
python3 <技能目录>/scripts/pr-comment.py -f <技能目录>/pr_review_report.md --parse-report
```

> **跨平台提示**：Windows 用户将 `python3` 替换为 `python`

**重要**：
- 仓库所有者和仓库名称需从 Clone 地址中提取（如 `git@gitcode.com:owner/repo.git` 中的 `owner` 和 `repo`）
- `--parse-report` 参数会自动解析报告，将潜在问题发布为行级评论，改进建议发布为整体评论
- 评论发布后，删除临时文件

**用户拒绝发布**：跳过此步骤，直接进入步骤 7。

---

## 📝 行级评论发布格式规范（关键！）

**重要**：为了让 `pr-comment.py` 脚本正确解析并发布行级评论，审查报告必须严格按照以下格式编写：

### 1. 问题章节位置

潜在问题必须放在 `### ⚠️ 潜在问题` 或 `### 潜在问题` 章节下。

### 2. 单个问题格式

每个问题必须包含以下元素：

```markdown
#### 序号。问题标题

```语言：文件路径#L 行号
代码片段
```

**风险等级**: 高 | 中 | 低

**问题描述**: 
问题的详细描述...

**建议**: 
改进建议...
```

### 3. 代码块格式（最关键！）

代码块必须严格遵循以下格式：

````markdown
```cpp:runtime/src/Interpreter/InterpreterSpecific.cpp#L227
    if (tlData == nullptr) {
        LOG(RTLOG_ERROR, "[Interpreter] IsPendingSafePoint called with null thread_local_data_t");
        return false;
    }
```
````

**格式要求**：
- ` ```语言：文件路径#L 行号`
- 语言：使用小写（`cpp`, `c`, `cj`, `python` 等）
- 文件路径：**相对路径**，从仓库根目录开始（如 `runtime/src/Interpreter/InterpreterSpecific.cpp`）
- 行号：使用 `#L 行号` 格式（如 `#L227`）
- 代码片段：必须是 PR 中实际修改的代码

### 4. 风险等级标注

必须明确标注风险等级：
```markdown
**风险等级**: 高
```
或
```markdown
**风险等级**: 中
```
或
```markdown
**风险等级**: 低
```

### 5. 完整示例

````markdown
### ⚠️ 潜在问题

#### 1. 线程安全问题 - 全局状态初始化

```cpp:runtime/src/Interpreter/InterpreterSpecific.cpp#L50
    interpreter_interface_t* operator->()
    {
        if (initialized) {
            return &interpreterInterface;
        }
        LOG(RTLOG_FATAL, "Usage of uninitialized interpreter interface\n");
        return nullptr;
    }
```

**风险等级**: 高

**问题描述**: 
`initialized` 标志不是原子变量，多线程环境下可能存在竞态条件。

**建议**: 
使用 `std::atomic<bool>` 或 `std::once_flag` 确保线程安全的初始化。

---

#### 2. 错误处理不完整 - 空指针检查

```cpp:runtime/src/Interpreter/InterpreterSpecific.cpp#L227
    if (tlData == nullptr) {
        LOG(RTLOG_ERROR, "[Interpreter] IsPendingSafePoint called with null thread_local_data_t");
        return false;
    }
```

**风险等级**: 中

**问题描述**: 
仅记录错误日志后返回 false，可能导致后续逻辑错误。

**建议**: 
```cpp
if (tlData == nullptr) {
    LOG(RTLOG_FATAL, "[Interpreter] IsPendingSafePoint called with null thread_local_data_t");
    abort();
}
```
````

### 6. 常见错误

| 错误 | 正确格式 | 说明 |
|------|----------|------|
| ` ```c:src/main.c#L10` | ` ```c:src/main.c#L10` | 文件路径必须是相对路径 |
| ` **风险等级**：高` | ` **风险等级**: 高` | 使用英文冒号 `:` |
| 缺少风险等级 | 必须标注 | 解析器依赖风险等级识别问题块 |
| 代码块无行号 | `#L 行号` | 行级评论需要行号 |
| 行号不在 diff 范围 | 检查实际 diff | GitCode API 会拒绝无效行号 |

### 7. 发布失败处理

如果行级评论发布失败，常见原因：

1. **行号不在 diff 范围内**
   - 使用 `git diff origin/main pr-<PR 号> -- 文件路径` 确认实际修改的行
   - 确保评论的行号在 diff 输出中

2. **文件路径错误**
   - 使用相对路径（从仓库根目录开始）
   - 检查文件名大小写

3. **代码块格式错误**
   - 确保格式为 ` ```语言：文件路径#L 行号`
   - 使用英文冒号 `:`

4. **PR 有多个提交**
   - 行号可能已变化
   - 使用 `git show pr-<PR 号>:文件路径 | head -n 行号 | tail -n 1` 验证

**失败处理**：
- 如果行级评论失败，整体评论仍然会发布
- 手动在 GitCode PR 页面添加行级评论
- 或者在整体评论中明确标注文件路径和行号

### 步骤 7: 清理和恢复（重要）

> **目的**：清理临时文件，恢复用户原有的工作状态。

---

**7.1 清理临时目录**（仅情况 B：新克隆的仓库）

**询问用户**：
> 审查已完成。是否需要删除临时克隆的仓库目录以释放磁盘空间？

- 如果用户同意删除：
  ```bash
  # 删除整个 pr_review 目录
  rm -rf "$(dirname "$REPO_DIR")"
  ```

- 如果用户选择保留，则保持目录不变

---

**7.2 恢复用户工作状态**（情况 A：用户已有仓库）

如果使用了用户已有的仓库目录，执行以下恢复操作：

1. **切换回原分支**：
   ```bash
   git -C "$REPO_DIR" checkout <ORIGINAL_BRANCH>
   ```

2. **恢复 stash 的修改**（如果 `HAS_STASH = true`）：
   ```bash
   # 检查是否有我们的 stash
   git -C "$REPO_DIR" stash list | grep "auto-stash-before-pr-review"

   # 如果有，恢复并删除 stash
   git -C "$REPO_DIR" stash pop
   ```

3. **确认恢复成功**：
   ```bash
   git -C "$REPO_DIR" status
   git -C "$REPO_DIR" branch --show-current
   ```

---

**恢复完成提示**：
> 已恢复到审查前的状态：
> - 当前分支：`<ORIGINAL_BRANCH>`
> - 工作区修改：已恢复（如之前有 stash）

---

**重要**：此步骤为流程的最后一步，必须确保用户的工作状态已恢复。

## 完整示例

详细命令示例请参阅: `references/examples.md`

## 注意事项

- **必须首先询问用户是否已有仓库目录**，避免重复克隆
- **必须记录仓库绝对路径**：克隆或进入仓库后，立即使用 `pwd` 记录 `REPO_DIR`，后续命令必须使用 `git -C "$REPO_DIR"` 语法，避免 Bash 会话隔离导致的路径丢失
- **检查并保护用户工作区状态**：有未提交修改时自动 stash，审查完成后恢复
- **审查完成后必须恢复用户工作状态**：切换回原分支，恢复 stash
- **必须基于完整文件内容进行审查**，而不仅仅是 diff 片段
- **必须执行修改全面性审查**，对照声称的修改点逐一验证
- **必须执行安全审查清单**，逐项检查所有安全检查项，不得遗漏
- **使用 Read 工具读取完整文件**，理解函数完整逻辑和上下文
- **审查完成后自动发布评论到 PR**，无需用户确认，包含潜在问题和改进建议（适合自动化场景如 openclaw）
- **行级评论格式必须严格遵循规范**：` ```语言：文件路径#L 行号`，风险等级必须标注
- **确保行号在 diff 范围内**：发布前使用 `git diff` 确认实际修改的行
- **必须验证 PR 实际变更范围**（关键！）：
  - ❌ **错误**：`git diff origin/dev review-<PR>` 会显示所有累积差异
  - ✅ **正确**：通过 GitCode API 获取实际变更文件数，或使用 `git diff $(git merge-base origin/dev review-<PR>) review-<PR>`
  - **原因**：PR 分支可能从目标分支的旧版本创建，直接 diff 会包含其他 PR 的变更
- 如果主分支名称不是 `main`（例如 `master`），需相应调整 diff 命令中的分支名
- 大型仓库克隆可能需要较长时间，请耐心等待
- 确保网络连接稳定以完成仓库克隆和 PR 分支获取
- 审查结果将以中文输出