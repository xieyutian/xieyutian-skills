# GitCode PR Comment 工作流程详解

本文档详细说明评论处理技能的完整工作流程，包括每一步的具体操作、异常处理和恢复机制。

## 目录

1. [完整工作流程](#完整工作流程)
2. [流程变量管理](#流程变量管理)
3. [异常处理](#异常处理)
4. [恢复机制](#恢复机制)

---

## 完整工作流程

### 步骤 0: 解析输入并获取本地仓库

**目标**: 从 PR URL 提取关键信息，获取或克隆本地仓库

**解析 PR URL**:
```
https://gitcode.com/<owner>/<repo>/pulls/<number>
→ owner, repo, number
```

**获取本地仓库路径**（自动处理缓存和克隆）:
```bash
python scripts/repo_cache.py --get "https://gitcode.com/<owner>/<repo>.git" --owner <owner> --repo <repo>
```

输出示例：
```json
{
  "local_path": "/path/to/gitcode_repos/<owner>_<repo>",
  "is_new_clone": true,
  "repo_url": "https://gitcode.com/<owner>/<repo>.git"
}
```

**处理逻辑**:
- `is_new_clone: false` → 缓存命中，直接使用缓存路径
- `is_new_clone: true` → 新克隆的仓库，已自动写入缓存

**设置变量**:
- `REPO_DIR = <local_path>`
- `HAS_LOCAL_REPO = true`

---

### 步骤 1: 准备工作环境

**目标**: 记录当前状态，保护用户工作区

仓库已在步骤 0 自动克隆（如需要），现在记录当前状态：

1. **记录原始信息**：
   ```bash
   git -C "$REPO_DIR" branch --show-current  # 当前分支
   ```
   **设置变量**: `ORIGINAL_BRANCH = <当前分支>`

2. **检查工作区状态**：
   ```bash
   git -C "$REPO_DIR" status
   ```

3. **处理未提交修改**（如有）：
   ```bash
   git -C "$REPO_DIR" stash push -m "auto-stash-before-pr-comment-$(date +%Y%m%d%H%M%S)"
   ```
   **设置变量**: `HAS_STASH = true`

---

### 步骤 2: 获取 PR 信息并检查权限

**目标**: 获取 PR 基本信息、文件变更和 commits，同时检查用户修改权限

```bash
python scripts/get_pr_info.py <token> <owner> <repo> <pr_number> --json
```

**输出内容**:
- PR 基本信息（标题、状态、源分支、目标分支）
- 文件变更列表
- Commits 信息
- PR 作者信息（用于权限检查）

**获取当前用户信息**（用于权限比对）:
```bash
# 通过 API 获取 Token 对应的用户信息
curl -s "https://api.gitcode.com/api/v5/user?access_token=<token>" | jq '.login'
```

**权限检查逻辑**:

比对 PR 作者（`pr_info.user`）与当前 Token 用户：

```markdown
## 权限检查结果

| 检查项 | 值 |
|--------|-----|
| PR 作者 | `pr_info.user` |
| 当前用户 | Token 用户名 |
| 是否匹配 | ✅/❌ |

**判断规则**:
- `pr_info.user == token_user` → **本人 PR**，有修改权限
- `pr_info.user != token_user` → **非本人 PR**，无直接修改权限
```

**设置变量**:
- `PR_BRANCH = <源分支名>`
- `PR_SHA = <源分支 SHA>`
- `PR_AUTHOR = <PR 作者>`
- `TOKEN_USER = <Token 用户>`
- `CAN_MODIFY = (PR_AUTHOR == TOKEN_USER)`

---

### 步骤 2.5: 权限分支处理

**根据权限检查结果，决定后续流程**：

**情况 A: 本人 PR（CAN_MODIFY = true）**

正常执行步骤 3-9，完整流程：
- 获取评论 → 切换分支 → 分析 → 修复 → 提交 → 回复

**情况 B: 非本人 PR（CAN_MODIFY = false）**

输出提醒信息，**流程终止**：

```
❌ 权限不足：此 PR 由 <PR_AUTHOR> 创建，您无权修改其代码。

建议操作：
- 如需处理评论问题，请联系 PR 作者
- 或等待 PR 作者自行处理

流程已终止。
```

> **重要**: 非本人 PR 无法 push 到源分支，不执行步骤 3-9，直接退出。

---

### 步骤 3: 获取 PR 评论

**目标**: 获取所有评论，提取讨论 ID 用于后续回复

```bash
python scripts/get_pr_comments.py <token> <owner> <repo> <pr_number> --analysis
```

**输出内容**:
- 所有评论（按类型分类）
- 评论内容、作者、时间、关联文件和行号
- 结构化数据（供 AI 分析使用）

**关键信息提取**:
- `discussion_id` - 用于线程式回复（长字符串）
- `comment_id` - 评论编号（数字）

---

### 步骤 4: 切换到 PR 分支

**目标**: 切换到 PR 源分支以便查看和修改代码

```bash
git -C "$REPO_DIR" fetch origin pull/<pr_number>/head:pr-comment-<pr_number>
git -C "$REPO_DIR" checkout pr-comment-<pr_number>
```

或使用 merge-requests 格式（部分平台）：
```bash
git -C "$REPO_DIR" fetch origin merge-requests/<pr_number>/head:pr-comment-<pr_number>
git -C "$REPO_DIR" checkout pr-comment-<pr_number>
```

---

### 步骤 5: 分析评论有效性（关键步骤）

> ⚠️ **核心原则**：**必须读取实际代码验证问题是否存在**，绝不依赖 commit message 判断！

#### 为什么不能信任 commit message

| 判断方式 | 问题 |
|----------|------|
| 根据 commit message "fix: 修复安全问题" | ❌ 可能只是部分修复、修复方式不当、甚至未真正修复 |
| 读取实际代码文件验证 | ✅ 确认问题是否真实存在、是否已正确修复 |

**真实案例教训**：

曾有评论指出 "硬编码密钥" 和 "IV 硬编码" 问题。看到 commit message 为 "fix: 修复安全问题"，误判问题已修复，回复了错误的 "已修复" 信息。实际检查代码发现：
- 密钥仍是硬编码 `let key = "xyt_commanderkey"`
- IV 仍是硬编码 `let iv = "commanderkey_xyt"`
- 问题并未修复！

**教训**：必须读取实际代码文件验证，不能轻信 commit message。

#### 代码验证流程

**步骤 5.1：读取评论引用的文件**

```bash
# 必须读取评论中提到的文件
Read: <repo_path>/<文件路径>
```

**步骤 5.2：对比评论引用的代码与实际代码**

逐个检查评论引用的代码位置，与实际代码对比：

```markdown
## 代码验证结果

| 评论序号 | 评论引用代码 | 实际代码（当前行） | 验证状态 |
|----------|--------------|-------------------|----------|
| 1 | `let key = "default_key"` | `let key = Env.get("KEY") ?? "default"` | ⚠️ 部分修复（仍有默认值） |
| 2 | `let iv = "fixed_iv"` | `let iv = "fixed_iv"` | ❌ 未修复 |
| 3 | `return None` (死代码) | `return None` | ❌ 未修复 |
| 4 | `硬编码密钥` | `let key = Env.get("KEY")` | ✅ 已修复 |
```

**步骤 5.3：输出分析报告**

**目标**: 验证评论提出的问题是否真实存在，基于实际代码判断

**核心分析任务**:

1. **过滤问题评论**:
   - 识别含有问题描述的评论（非感谢、确认类评论）
   - 提取文件路径、行号、问题描述

2. **验证问题有效性**:
   - 读取本地代码文件（使用 Read 工具）
   - 检查评论提到的代码位置
   - 结合 PR diff 验证问题是否在 PR 新增代码中

3. **输出分析报告**:

```markdown
## 评论分析报告

### 有效问题（需要处理）
| 序号 | 评论ID | 讨论ID | 文件 | 行号 | 问题类型 | 问题描述 | 验证结果 |
|------|--------|--------|------|------|----------|----------|----------|
| 1 | 165980011 | b66f1e2e... | src/secret_store.cj | 10-12 | 🔴 高风险 | 硬编码加密密钥 | ✅ 确认存在 |
| 2 | 165980012 | a55f3d2e... | src/secret_store.cj | 13-14 | 🟡 中风险 | 路径遍历风险 | ✅ 确认存在 |

> **关键**: 必须记录每个问题的 **discussion_id**（长字符串），用于后续线程式回复！

### 非问题评论（无需处理）
| 序号 | 评论ID | 评论内容 | 非问题原因 |
|------|--------|----------|------------|
| 1 | 165980015 | "代码看起来不错" | 无实质问题，无需处理 |

### 待确认评论
| 序号 | 评论ID | 讨论ID | 评论内容 | 需要用户确认的原因 |
|------|--------|--------|----------|-------------------|
| 1 | 165980016 | d88h5g4e... | "建议重构此函数" | 涉及设计决策，需要用户判断 |
```

**设置变量**: `ISSUE_DISCUSSION_MAP = {"b66f1e2e...": "硬编码密钥", "a55f3d2e...": "路径遍历", ...}`

---

### 步骤 5.5: 修复方案设计（Plan 子 agent）

**目标**: 使用 Plan 子 agent 深度分析问题根因，设计高质量修复方案

#### 为什么使用子 agent

| 对比项 | 主 agent 直接设计 | Plan 子 agent 设计 |
|--------|-------------------|-------------------|
| 思考深度 | 快速提出方案，可能不够深入 | 专门分析，深度思考 |
| 方案数量 | 通常只提一个方案 | 可提出多个备选方案 |
| 优缺点评估 | 缺乏系统评估 | 系统评估每个方案 |
| 问题根因 | 可能忽略根因 | 深入分析根因 |
| 上下文影响 | 可能忽略相关代码 | 全面考虑相关模块 |

#### 子 agent 调用方式

使用 Agent 工具启动 Plan 子 agent：

```
Agent 工具调用：
- subagent_type: "Plan"
- description: "设计 PR 评论问题修复方案"
- prompt: "
  任务：为以下 PR 评论问题设计修复方案
  
  ## 问题列表
  <从步骤 5 获取的有效问题列表，含文件路径、行号、问题描述>
  
  ## 代码上下文
  <相关文件内容、PR diff 信息>
  
  ## 设计要求
  1. 分析每个问题的根本原因
  2. 考虑多种可能的修复方案（至少 2 个）
  3. 评估每种方案的优缺点
  4. 推荐最佳方案并说明理由
  5. 提供具体的代码修改建议
  
  ## 输出格式
  对每个问题输出：
  - 问题根因分析
  - 方案选项（至少 2 个，含代码示例）
  - 推荐方案 + 选择理由
  - 影响范围评估（相关模块、文档更新需求）
  "
```

#### 子 agent 输出格式示例

```markdown
## 问题 #1: 硬编码加密密钥

### 根因分析
密钥直接硬编码在源码中，存在以下风险：
- 代码泄露即密钥泄露
- 无法针对不同环境使用不同密钥
- 不符合安全最佳实践

### 方案选项

**方案 A: 环境变量 + 强制配置**
```cj
let keyStr = Env.get("ENCRYPTION_KEY")
if (keyStr.isNone()) {
    throw Exception("ENCRYPTION_KEY 未设置，请配置后再使用")
}
let key = keyStr.getOrThrow()
```
优点：安全性高，强制用户配置
缺点：需要用户预先设置环境变量

**方案 B: 环境变量 + 默认值（不推荐）**
```cj
let key = Env.get("ENCRYPTION_KEY") ?? "default_key_16bytes"
```
优点：使用方便
缺点：默认密钥可预测，安全性不足

### 推荐方案
**方案 A**，理由：安全性优先，避免弱密钥风险

### 影响范围
- 需更新文档说明环境变量配置方法
- 需更新测试代码适配新的初始化逻辑
```

#### 设置变量

| 变量 | 说明 |
|------|------|
| `FIX_PLANS` | 子 agent 输出的完整方案设计（Markdown 格式） |
| `PLAN_COMPLETED` | `true` |

---

### 步骤 5.6: 修复方案确认

**目标**: 向用户展示 Plan 子 agent 设计的方案，让用户审核并确认

#### 方案汇总展示

汇总所有问题的推荐方案，便于用户快速审核：

```
步骤 5.5 已完成: 修复方案设计 (Plan 子 agent)

## 修复方案汇总

### 问题 #1: 硬编码加密密钥
推荐方案: 环境变量 + 强制配置
修复说明: 未设置环境变量时抛出异常

### 问题 #2: IV 硬编码
推荐方案: 随机 IV + 与密文一起存储
修复说明: 每次加密生成随机 IV，解密时从数据中提取

### 问题 #3: 密钥长度验证
推荐方案: 添加 16 字节长度检查
修复说明: SM4 要求 128 位密钥，不符合时抛出异常

### 问题 #4: 文件末尾换行符
推荐方案: 添加末尾空行
修复说明: 符合 POSIX 标准
```

#### 用户确认选项

使用 AskUserQuestion 工具提供以下选项：

| 选项 | 说明 |
|------|------|
| 采用所有推荐方案 | 批量确认所有修复方案，直接执行修复 |
| 逐个审核方案 | 每个问题单独展示详细方案，逐个确认 |
| 查看方案详情 | 展示完整的方案设计输出（含根因分析、方案对比） |
| 我有其他修改方案 | 用户提供自定义修复代码 |

#### 逐个审核流程

当用户选择"逐个审核方案"时，对每个问题单独展示：

```
问题 #1: 硬编码加密密钥
讨论 ID: b66f1e2e...
文件: src/secret_store.cj
行号: 10-12
风险等级: 🔴 高风险

根因分析: 密钥硬编码存在泄露风险，无法针对不同环境配置...

推荐方案:
```cj
let keyStr = Env.get("ENCRYPTION_KEY")
if (keyStr.isNone()) {
    throw Exception("ENCRYPTION_KEY 未设置")
}
let key = keyStr.getOrThrow()
```

> 是否采用此方案？
```

使用 AskUserQuestion 让用户选择：
- **采用推荐方案** - 使用子 agent 推荐的方案
- **查看备选方案** - 展示其他方案选项
- **自定义方案** - 用户输入自己的修复代码

#### 设置变量

| 变量 | 说明 |
|------|------|
| `CONFIRMED_FIXES` | 用户确认的修复方案列表 |
| `USER_CONFIRMED` | `true` |

> **重要**: 用户确认后才执行修复，不自动修改代码！

---

### 步骤 6: 问题修复流程

**目标**: 逐个修复有效问题，记录修复与讨论 ID 的对应关系

对于每个有效问题：

**展示问题详情**:
```
问题 #1: 空指针未检查
评论 ID: 12345
文件: src/main.c
行号: 50

当前代码:
```c
if (ptr != NULL) {  // 原代码有逻辑错误
    process(ptr);
}
```

建议修复方案:
```c
if (ptr == NULL) {
    return -1;
}
process(ptr);
```
```

**询问用户确认**:
> 是否采用此修复方案？或者您有其他修改方式？

**执行修复**（用户确认后）:
- 使用 Edit 工具修改代码
- **记录修复与 discussion_id 的对应关系**:
  ```python
  FIXED_ISSUE_MAP = [
    {"discussion_id": "b66f1e2e...", "issue": "硬编码密钥", "fix": "密钥改为从环境变量获取"},
    {"discussion_id": "a55f3d2e...", "issue": "路径遍历", "fix": "添加 key 参数验证"}
  ]
  ```

> **关键**: 每修复一个问题，必须记录其 **discussion_id** 和具体修复说明！

---

### 步骤 7: 提交修复更新

**目标**: 合并所有修复为单次提交并推送

所有修复完成后，合并为单次提交：

```bash
git -C "$REPO_DIR" add <所有修改的文件>
git -C "$REPO_DIR" commit -m "fix: 根据 PR #<pr_number> 评论修复问题

修复内容:
- <文件1>: <问题描述1>
- <文件2>: <问题描述2>"
git -C "$REPO_DIR" push origin pr-comment-<pr_number>
```

获取提交 SHA：
```bash
git -C "$REPO_DIR" log -1 --format="%H"
```

**设置变量**: `COMMIT_SHA = <提交 SHA>`

---

### 步骤 8: 回复评论说明已修复

**目标**: 回复每个修复的评论，发布修复总结

**首先回复每个修复的评论（使用 discussion_id）**:
```bash
python scripts/post_comment_reply.py <token> <owner> <repo> <pr_number> \
  --detailed-replies '{"b66f1e2e...": "密钥改为从环境变量获取", "a55f3d2e...": "添加路径遍历验证"}'
```

> **重要**: 使用 `--detailed-replies` 参数，键是 **discussion_id**（长字符串）。

**然后发布修复总结评论**:
```bash
python scripts/post_comment_reply.py <token> <owner> <repo> <pr_number> \
  --summary --commit-sha "<commit_sha>" \
  --fixed-issues "硬编码加密密钥,文件路径遍历风险"
```

---

### 步骤 9: 清理和恢复

**目标**: 恢复用户工作区状态

**恢复用户工作状态**:

1. 切换回原分支：
   ```bash
   git -C "$REPO_DIR" checkout <ORIGINAL_BRANCH>
   ```

2. 恢复 stash（如有）：
   ```bash
   git -C "$REPO_DIR" stash pop
   ```

3. 清理临时目录（如是新克隆的仓库）：
   - 询问用户是否删除

**恢复完成提示**:
> 已恢复到处理前的状态：
> - 当前分支：`<ORIGINAL_BRANCH>`
> - 工作区修改：已恢复

---

## 流程变量管理

执行过程中需记录以下变量：

| 变量名 | 说明 | 设置时机 | 示例值 |
|--------|------|----------|--------|
| `REPO_DIR` | 仓库的绝对路径 | 步骤 0 | `/path/to/local/repo` |
| `OWNER` | 仓库所有者 | 步骤 0 | `<owner>` |
| `REPO` | 仓库名称 | 步骤 0 | `<repo>` |
| `PR_NUMBER` | PR 编号 | 步骤 0 | `123` |
| `HAS_LOCAL_REPO` | 是否使用用户已有仓库 | 步骤 0 | `true/false` |
| `ORIGINAL_BRANCH` | 用户原始分支名 | 步骤 1 | `main` |
| `HAS_STASH` | 是否执行了 stash | 步骤 1 | `true/false` |
| `PR_BRANCH` | PR 源分支名 | 步骤 2 | `feature-branch` |
| `PR_SHA` | PR 源分支 SHA | 步骤 2 | `abc123` |
| `PR_AUTHOR` | PR 作者 | 步骤 2 | `<pr_author>` |
| `TOKEN_USER` | Token 对应的用户名 | 步骤 2 | `<token_user>` |
| `CAN_MODIFY` | 是否有修改权限 | 步骤 2 | `true/false` |
| `ISSUE_DISCUSSION_MAP` | 问题与讨论 ID 映射 | 步骤 5 | `{"abc123...": "问题描述"}` |
| `FIX_PLANS` | 子 agent 输出的完整方案设计 | 步骤 5.5 | `Markdown 格式` |
| `PLAN_COMPLETED` | 方案设计是否完成 | 步骤 5.5 | `true/false` |
| `CONFIRMED_FIXES` | 用户确认的修复方案列表 | 步骤 5.6 | `[{"issue": "...", "plan": "..."}]` |
| `USER_CONFIRMED` | 用户是否已确认方案 | 步骤 5.6 | `true/false` |
| `FIXED_ISSUE_MAP` | 修复与讨论 ID 映射 | 步骤 6 | `[{"discussion_id": "...", "fix": "..."}]` |
| `COMMIT_SHA` | 修复提交 SHA | 步骤 7 | `b7da6d8` |

---

## 异常处理

### 步骤 0: 仓库获取失败

**克隆失败原因**:
- 网络连接问题
- 仓库权限不足
- 仓库不存在

**处理方式**:
```bash
# 检查网络
ping gitcode.com

# 检查仓库 URL 是否正确
# 尝试手动克隆以获取详细错误信息
git clone <repo_url>
```

**恢复**: 提示用户检查网络和权限，退出流程。

---

### 步骤 1: Git 状态异常

**工作区有冲突**:
```bash
# 检查冲突状态
git -C "$REPO_DIR" status

# 如果有未解决的冲突，提示用户先解决
```

**处理方式**: 提示用户先解决冲突，再继续流程。

---

### 步骤 2: 权限检查结果 - 非本人 PR

**检测到非本人 PR**:
- PR 作者与 Token 用户不匹配
- 用户无权 push 到 PR 源分支

**处理方式**: 输出提醒信息，流程终止

```
❌ 权限不足：此 PR 由 <PR_AUTHOR> 创建，您无权修改其代码。

建议操作：
- 如需处理评论问题，请联系 PR 作者
- 或等待 PR 作者自行处理

流程已终止。
```

> **注意**: 不执行后续步骤，直接退出流程。

---

### 步骤 4: 分支切换失败

**fetch 失败**:
- 网络问题：检查连接后重试
- 权限问题：确认 Token 有效

```bash
# 重试 fetch
git -C "$REPO_DIR" fetch origin --verbose
```

**checkout 失败**:
- 分支已存在但有冲突：
  ```bash
  # 删除旧分支后重新创建
  git -C "$REPO_DIR" branch -D pr-comment-<pr_number>
  git -C "$REPO_DIR" fetch origin pull/<pr_number>/head:pr-comment-<pr_number>
  ```

---

### 步骤 7: Push 失败

**Push 被拒绝原因**:
- 分支权限不足
- 远程有新提交（冲突）

**处理方式**:
```bash
# 检查远程状态
git -C "$REPO_DIR" fetch origin
git -C "$REPO_DIR" log origin/pr-comment-<pr_number>..HEAD

# 如果有冲突，提示用户手动处理
if [ 有冲突 ]; then
    echo "远程有新提交，需要手动合并或 rebase"
fi
```

**恢复**: 提示用户手动处理冲突后 push，继续步骤 8。

---

### 步骤 8: 评论回复失败

**API 错误**:
- 401: Token 无效或过期
- 404: 评论不存在或已被删除
- 500: GitCode 服务问题

**处理方式**:
```bash
# 验证 Token
python scripts/get_pr_comments.py <token> <owner> <repo> <pr_number> --json

# 如果 Token 过期，提示用户更新
```

**部分回复失败**: 记录失败的 discussion_id，提示用户手动回复。

---

### 步骤 9: 恢复失败

**stash pop 失败**:
- 工作区有新修改导致冲突

**处理方式**:
```bash
# 查看 stash 内容
git -C "$REPO_DIR" stash show -p

# 手动处理冲突
git -C "$REPO_DIR" stash pop
# 或丢弃 stash（如果用户同意）
git -C "$REPO_DIR" stash drop
```

---

## 恢复机制

### 全局恢复点

如果流程在任何步骤中断，执行以下恢复操作：

```bash
# 1. 检查是否在临时分支
CURRENT_BRANCH=$(git -C "$REPO_DIR" branch --show-current)
if [ "$CURRENT_BRANCH" == "pr-comment-<pr_number>" ]; then
    # 切换回原分支
    git -C "$REPO_DIR" checkout $ORIGINAL_BRANCH
fi

# 2. 检查是否有 stash
if [ "$HAS_STASH" == "true" ]; then
    git -C "$REPO_DIR" stash pop
fi

# 3. 清理临时分支（可选）
git -C "$REPO_DIR" branch -D pr-comment-<pr_number>
```

### 状态检查清单

流程完成后检查：

| 检查项 | 命令 | 期望结果 |
|--------|------|----------|
| 当前分支 | `git branch --show-current` | `ORIGINAL_BRANCH` |
| 工作区干净 | `git status` | 无未提交修改（或有 stash 恢复） |
| 修复已推送 | `git log -1 --oneline origin/pr-comment-<pr_number>` | 包含修复提交 |
| 评论已回复 | 查看 PR 页面 | 每个修复都有回复 |

---

## 进度提示

执行过程中，每完成一步输出：

> ✅ 步骤 N/9 完成: <步骤名称>

例如：
```
✅ 步骤 0/9 完成: 解析输入并获取本地仓库
✅ 步骤 1/9 完成: 准备工作环境
✅ 步骤 2/9 完成: 获取 PR 信息
✅ 步骤 3/9 完成: 获取 PR 评论 (5 条)
✅ 步骤 4/9 完成: 切换到 PR 分支
✅ 步骤 5/9 完成: 分析评论有效性 (3 个有效问题)
✅ 步骤 5.5/9 完成: 修复方案设计 (Plan 子 agent)
✅ 步骤 5.6/9 完成: 方案确认 (用户已审核)
✅ 步骤 6/9 完成: 问题修复 (修复了 3 个问题)
✅ 步骤 7/9 完成: 提交修复更新 (SHA: b7da6d8)
✅ 步骤 8/9 完成: 回复评论说明已修复
✅ 步骤 9/9 完成: 清理和恢复
```