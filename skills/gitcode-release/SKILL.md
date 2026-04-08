---
name: gitcode-release
description: GitCode 平台发行版（Release）自动创建技能。当用户提到"创建发行版"、"发布 Release"、"打 Tag 发布"、"创建 GitCode Release"、"新建发行版"、"发版"时触发。自动分析本地 Git 仓库信息，推断版本号，生成发行版描述，创建 Tag 和 Release。必须提供 GitCode Token。
---

# GitCode Release

基于本地 Git 仓库信息，自动在 GitCode 平台创建发行版（Release）。自动推断版本号，根据合入修改生成发行版描述。

## 使用前提

- 系统已安装 Git 和 Python3（含 requests 库）
- 已配置 GitCode Token
- 当前工作目录为 Git 仓库（或提供仓库路径）

## 输入参数

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| GitCode Token | 个人访问令牌 | 是 | `your-token` |
| 本地仓库路径 | Git 仓库目录 | 否* | `/home/user/myproject` |
| 指定版本号 | 手动指定 tag 版本号（跳过自动推断） | 否 | `v2.1.0` |
| 目标分支 | tag 打在哪个分支/commit 上 | 否 | `main` |

> *注：不提供则使用当前工作目录。

## 流程变量

执行中需记录以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `REPO_DIR` | 本地仓库绝对路径 | `/home/user/myproject` |
| `OWNER` | 仓库所有者 | `xieyutian` |
| `REPO` | 仓库名称 | `xyt_commander` |
| `ACCESS_TOKEN` | GitCode Token | `your-token` |
| `LATEST_TAG` | 最新的已有 tag | `v2.0.0` |
| `NEW_TAG` | 推断/确认的新 tag | `v2.1.0` |
| `TARGET_COMMITISH` | 目标分支或 commit | `main` |
| `RELEASE_BODY_FILE` | 发行版描述临时文件路径 | `/tmp/release_body.md` |

---

## 创建流程

### 步骤 0: 解析本地仓库信息

**目的**：从本地 Git 仓库自动获取 owner/repo。

**执行操作**：

1. 确认当前目录是 Git 仓库（或使用用户提供的路径）
   ```bash
   git -C "$REPO_DIR" rev-parse --is-inside-work-tree
   ```

2. 获取 remote URL 并解析 owner/repo
   ```bash
   git -C "$REPO_DIR" remote -v
   ```

3. 从 remote URL 解析 owner/repo，支持以下格式：
   - SSH: `git@gitcode.com:<owner>/<repo>.git` → owner, repo
   - HTTPS: `https://gitcode.com/<owner>/<repo>.git` → owner, repo
   - 无后缀: `https://gitcode.com/<owner>/<repo>` → owner, repo

4. 如果不是 gitcode.com 的仓库，询问用户确认 owner/repo

5. **更新远程引用和 Tags**（必须先 fetch，避免本地分支/tag 过期导致误判和 git log 报错）：
   ```bash
   git -C "$REPO_DIR" fetch origin --tags
   ```

6. 确认分支状态：
   ```bash
   git -C "$REPO_DIR" branch --show-current
   git -C "$REPO_DIR" status --short
   ```

7. 如果有未提交修改，**提醒用户**（发行版基于 commit 创建，不影响工作区，但建议在干净状态下操作）

8. 检查目标分支与当前分支的同步状态时，**必须使用远程跟踪分支**（`origin/<branch>`），而非本地分支名，因为本地分支可能过期：
   ```bash
   # 正确：使用远程跟踪分支对比
   git -C "$REPO_DIR" log origin/main..origin/dev --oneline --no-merges

   # 错误：本地 main 可能长期未更新，导致误判
   # git log main..dev  ← 不要这样做
   ```

### 步骤 1: 获取版本历史

**目的**：收集版本历史信息，用于推断新版本号。

**获取已有 Tags**：
```bash
python3 "<技能目录>/scripts/create_release.py" "$ACCESS_TOKEN" "$OWNER" "$REPO" --get-tags
```

**获取最新 Release**：
```bash
python3 "<技能目录>/scripts/create_release.py" "$ACCESS_TOKEN" "$OWNER" "$REPO" --get-latest-release
```

**收集自上个 tag 以来的 commit 历史**（如果存在上个 tag）：
```bash
# 简要 commit 列表
git -C "$REPO_DIR" log "$LATEST_TAG"..HEAD --oneline --no-merges

# 带 PR 信息的 merge commit
git -C "$REPO_DIR" log "$LATEST_TAG"..HEAD --merges --oneline

# 完整 commit 信息（含作者）
git -C "$REPO_DIR" log "$LATEST_TAG"..HEAD --format="%h %s (%an)" --no-merges

# 变更统计
git -C "$REPO_DIR" diff "$LATEST_TAG"..HEAD --stat
```

**首个 tag（无历史 tag）时**，收集最近的 commit：
```bash
git -C "$REPO_DIR" log --oneline --no-merges -30
git -C "$REPO_DIR" log --format="%h %s (%an)" --no-merges -30
```

### 步骤 2: 推断版本号

**目的**：基于 conventional commits 前缀自动推断新版本号。

**推断规则**：

| 条件 | 版本升级 | 示例 |
|------|----------|------|
| 包含 `BREAKING CHANGE` 或 `!:` 前缀 | major | `v1.0.0` → `v2.0.0` |
| 包含 `feat:` 或 `feature:` 前缀 | minor | `v1.0.0` → `v1.1.0` |
| 仅 `fix:` 及其他 | patch | `v1.0.0` → `v1.0.1` |
| 无历史 tag | 首个版本 | `v1.0.0` |

**版本号解析**：
- 从 tag 中提取 semver：正则 `(\d+)\.(\d+)\.(\d+)`
- 支持 `v1.2.3`、`1.2.3`、`release-1.2.3` 格式
- 忽略非 semver 格式的 tag（如 `latest`、`stable`）
- 保持历史 tag 的前缀风格（`v` 前缀或不加）

**展示推断结果**：
```
当前最新 Tag: v2.0.0
推荐新版本号: v2.1.0
推断理由: 检测到新功能添加（feat:），建议 minor 版本升级

Commit 分析:
- feat: 3 个（新功能）
- fix: 5 个（修复）
- refactor: 2 个（重构）
- docs: 1 个（文档）
```

**询问用户**：
- 使用推断的版本号？
- 手动指定版本号？

### 步骤 3: 生成描述、确认并创建发行版

**目的**：基于 git log 生成发行版描述，展示完整信息供用户一次性确认，然后创建。

**3.1 生成发行版描述**

Claude 参考 [release-template.md](references/release-template.md) 模板，将收集到的 commit 信息按以下规则分类整理：

1. 按 conventional commit 前缀分类（feat→新功能, fix→修复, refactor→改进, 其他）
2. 去除 commit 前缀（如 `feat:`, `fix:`），保留描述内容
3. 从 merge commit 提取 PR 编号
4. 过滤无实质意义的 commit（如 "wip", "fix typo"）
5. 按模板格式组织
6. 生成比较链接：`https://gitcode.com/{owner}/{repo}/compare/{上个tag}...{新tag}`

**3.2 展示确认信息并询问用户**

一次性展示完整信息：
```
发行版创建确认:

Tag 名称: v2.1.0
发行版标题: v2.1.0 - 新增用户认证功能
目标分支: main

发行版描述:
  (预览生成的描述内容)
```

用户可以：
- **直接确认创建** — 使用当前描述创建
- **修改描述** — 手动调整后再确认
- **取消** — 放弃创建

**3.3 用户确认后执行**

1. 将描述写入临时文件（使用 Write 工具，不用 shell heredoc）
2. 调用创建 API：
   ```bash
   python3 "<技能目录>/scripts/create_release.py" "$ACCESS_TOKEN" "$OWNER" "$REPO" \
     --create-release \
     --tag-name "$NEW_TAG" \
     --name "{发行版标题}" \
     --body-file "$RELEASE_BODY_FILE" \
     --target-commitish "$TARGET_COMMITISH"
   ```

3. 创建成功后清理临时文件

### 步骤 4: 验证创建结果

**目的**：确认发行版已成功创建。

```bash
python3 "<技能目录>/scripts/create_release.py" "$ACCESS_TOKEN" "$OWNER" "$REPO" \
  --get-release --tag "$NEW_TAG"
```

**展示结果**：
- Release 链接
- Tag 名称
- 创建时间

**创建失败处理**：

如果创建 API 返回错误，根据错误类型采取不同策略：
- **409 冲突（Tag 已存在）**：提示用户 Tag 已被占用，建议更换版本号或删除已有 Tag
- **422 验证失败**：检查参数格式，修正后重试
- **401 认证失败**：提示用户检查 Token 是否正确或已过期
- **Tag 已创建但 Release 创建失败**：提示用户远程已有孤立 Tag，可通过 `git push origin --delete <tag>` 删除后重试，或直接基于该 Tag 重新创建 Release

---

## 版本号推断详细逻辑

### Semver 解析

从 tag 列表中筛选符合 semver 格式的 tag：

```
1. 遍历所有 tags
2. 使用正则 r'(\d+)\.(\d+)\.(\d+)' 匹配
3. 找出版本号最大的 tag 作为 latest
4. 保留前缀（v 或无前缀）
```

### 升级判定

```
优先级: BREAKING CHANGE > feat > fix

遍历所有新 commit:
  - 消息含 "BREAKING CHANGE" 或匹配 "^\w+!:" → has_breaking = True
  - 前缀为 "feat:" 或 "feature:" → has_feat = True
  - 其他前缀 → has_fix = True

if has_breaking: major 升级
elif has_feat: minor 升级
else: patch 升级
```

### 边界情况

- **无历史 tag**：建议 `v1.0.0`
- **所有 tag 不符合 semver**：建议 `v1.0.0`
- **用户手动指定版本号**：跳过推断，直接使用
- **tag 已存在**：在创建前通过 `--get-tags` 检查，提示用户

---

## 注意事项

- **必须在 Git 仓库中执行**：步骤 0 会验证当前目录是否为 Git 仓库
- **必须先 fetch**：步骤 0 中必须执行 `git fetch origin --tags`，同步远程分支和 Tags，避免本地过期导致误判或 git log 报错
- **remote URL 解析**：正确处理 SSH 和 HTTPS 两种格式，以及 `.git` 后缀的有无
- **Tag 前缀**：建议使用 `v` 前缀的 semver 格式，与历史 tag 保持一致
- **tag 已存在**：创建前检查，避免 API 报 409 冲突
- **target_commitish**：默认为当前分支 HEAD；如果 tag 不存在，API 会自动基于此参数创建 tag
- **发行版描述**：不应包含敏感信息（密钥、token 等）
- **Token 安全**：不将 Token 写入文件或日志

## 脚本命令速查

```bash
# 获取全部 Tags（自动翻页）
python3 scripts/create_release.py <token> <owner> <repo> --get-tags

# 获取最新 Release
python3 scripts/create_release.py <token> <owner> <repo> --get-latest-release

# 获取指定 Tag 的 Release
python3 scripts/create_release.py <token> <owner> <repo> --get-release --tag v1.0.0

# 获取全部 Releases（自动翻页）
python3 scripts/create_release.py <token> <owner> <repo> --get-releases

# 创建发行版
python3 scripts/create_release.py <token> <owner> <repo> \
  --create-release \
  --tag-name "v1.0.0" \
  --name "v1.0.0 - 首个版本" \
  --body-file release_body.md \
  --target-commitish "main"

# 使用环境变量
export GITCODE_TOKEN="<token>"
export REPO_OWNER="<owner>"
export REPO_NAME="<repo>"
python3 scripts/create_release.py --get-tags

# JSON 输出
python3 scripts/create_release.py <token> <owner> <repo> --get-tags --json
```

## 与其他技能的关系

- **gitcode-api-helper**：可通过此技能查询 Release 和 Tag API 的详细文档
- **gitcode-pr-review**：审查代码质量 → **gitcode-release**：审查通过后发布发行版
- **gitcode-pr-comment**：处理 PR 评论 → 修复后可触发创建发行版

## 参考文件

| 文件 | 用途 |
|------|------|
| [release-template.md](references/release-template.md) | 发行版描述模板和分类规则 |
| [examples.md](references/examples.md) | 完整使用示例 |
