# 完整示例

> **跨平台提示**：
> - Windows 用户将 `python3` 替换为 `python`
> - Windows 用户需要使用 Git Bash 或 WSL 执行 bash 命令

> **重要**：由于 Bash 会话隔离，每个 Bash 命令都是独立的 shell，`cd` 不会持久化。因此：
> - 所有 git 命令必须使用 `git -C "$REPO_DIR"` 语法
> - 克隆后必须立即使用 `pwd` 记录 `REPO_DIR` 绝对路径

## 示例 A：用户已有仓库目录

假设用户提供：
- 本地仓库路径: `/home/user/cangjie_runtime`
- PR 编号: `1028`

执行命令序列：

```bash
# 0. 记录仓库绝对路径（关键！）
REPO_DIR="/home/user/cangjie_runtime"

# 记录原始状态
ORIGINAL_BRANCH=$(git -C "$REPO_DIR" branch --show-current)  # 例如: main
ORIGINAL_DIR="$REPO_DIR"

# 检查工作区状态
git -C "$REPO_DIR" status
# 如果有未提交的修改，执行 stash
git -C "$REPO_DIR" stash push -m "auto-stash-before-pr-review-$(date +%Y%m%d%H%M%S)"

# 3. 获取 PR 分支
git -C "$REPO_DIR" fetch https://gitcode.com/Cangjie/cangjie_runtime.git merge-requests/1028/head:review-1028

# 4. 切换分支
git -C "$REPO_DIR" checkout review-1028

# 4.5. 获取 PR 审查上下文（通过 API）
python3 <技能目录>/scripts/get_pr_info.py <token> Cangjie cangjie_runtime 1028

# 5. 执行审查（同上）
# ...

# 6. 展示审查报告，询问用户是否发布

# 7. 清理和恢复
# 7.1 不需要清理（使用的是用户已有仓库）

# 7.2 恢复用户工作状态
git -C "$REPO_DIR" checkout main  # 切换回原分支
git -C "$REPO_DIR" stash pop      # 恢复未提交的修改

# 确认恢复
git -C "$REPO_DIR" status
git -C "$REPO_DIR" branch --show-current
```

---

## 示例 B：用户没有仓库目录

假设用户提供：
- 仓库地址: `https://gitcode.com/Cangjie/cangjie_runtime.git`
- PR 编号: `1028`

执行命令序列：

```bash
# 1-2. 创建目录并克隆仓库（链式命令确保在同一 shell 执行）
mkdir -p pr_review && cd pr_review && git clone https://gitcode.com/Cangjie/cangjie_runtime.git

# 记录仓库绝对路径（关键！）
# 假设当前工作目录是 /home/user，克隆后仓库路径为：
REPO_DIR="/home/user/pr_review/cangjie_runtime"
# 或使用 pwd 获取：
# REPO_DIR="$(pwd)/cangjie_runtime"

# 验证克隆成功
git -C "$REPO_DIR" status

# 3. 获取 PR 分支
git -C "$REPO_DIR" fetch https://gitcode.com/Cangjie/cangjie_runtime.git merge-requests/1028/head:review-1028

# 4. 切换分支
git -C "$REPO_DIR" checkout review-1028

# 4.5. 获取 PR 审查上下文（通过 API）
python3 <技能目录>/scripts/get_pr_info.py <token> Cangjie cangjie_runtime 1028
# 输出会显示 PR 的声称修改点、文件变更等信息

# 5. 执行审查
# 5.1 获取变更文件列表
python3 <技能目录>/scripts/get_pr_info.py <token> Cangjie cangjie_runtime 1028 --files

# 5.2 读取变更文件的完整内容（使用 Read 工具）
# 例如：Read 文件路径 $REPO_DIR/stdlib/libs/std/net/native/socket_buffer.c
# 这样可以看到完整函数定义和上下文

# 5.3 查看 diff 了解具体修改
git -C "$REPO_DIR" diff main...review-1028 --stat
git -C "$REPO_DIR" diff main...review-1028

# 5.4 执行安全审查清单检查
grep -rnE "(key|secret|password|token|iv)\s*=\s*[\"']" "$REPO_DIR/stdlib/libs/std/net/"
grep -rnE "(encrypt|decrypt|hash|crypto|auth)" "$REPO_DIR/stdlib/libs/std/net/"

# 5.5 对照声称的修改点，验证修改全面性和正确性
# 基于完整文件内容和审查结果，按照「审查报告格式规范」输出报告

# 6. 展示审查报告，询问用户是否发布到 PR
# 如果用户确认发布：
export GITCODE_TOKEN="your-token"
export REPO_OWNER="Cangjie"
export REPO_NAME="cangjie_runtime"
export PR_NUMBER="1028"
python3 <技能目录>/scripts/pr-comment.py -f <技能目录>/pr_review_report.md --parse-report
# 发布成功后删除临时文件
rm -f <技能目录>/pr_review_report.md
# 如果用户拒绝发布，跳过此步骤

# 7. 清理和恢复
# 7.1 询问用户是否清理临时目录
# 如果用户同意：
rm -rf "$(dirname "$REPO_DIR")"  # 删除 pr_review 目录
# 如果用户拒绝，则保留目录

# 7.2 不需要恢复（使用的是新克隆的仓库）
```

---

## Claude Code 执行示例

在实际 Claude Code 会话中，执行流程如下：

### 用户没有仓库目录的情况

```
Claude: 我来审查这个 PR。首先克隆仓库并记录绝对路径。

Bash: mkdir -p pr_review && cd pr_review && git clone https://gitcode.com/xieyutian/xyt_commander.git && pwd
输出: Cloning into 'xyt_commander'...
      /c/code/xyt_skill/pr_review

Claude: 克隆完成。记录 REPO_DIR = /c/code/xyt_skill/pr_review/xyt_commander

Bash: git -C "/c/code/xyt_skill/pr_review/xyt_commander" fetch https://gitcode.com/xieyutian/xyt_commander.git merge-requests/3/head:review-3
输出: From https://gitcode.com/xieyutian/xyt_commander
      * [new ref]         refs/merge-requests/3/head -> review-3

Bash: git -C "/c/code/xyt_skill/pr_review/xyt_commander" checkout review-3
输出: Switched to branch 'review-3'

Claude: 已切换到审查分支，继续获取 PR 信息...
```

### 关键点

1. **链式命令**：`mkdir && cd && git clone && pwd` 确保在同一 shell 执行
2. **记录路径**：克隆后立即使用 `pwd` 获取绝对路径
3. **使用绝对路径**：后续所有 git 命令使用 `git -C "$REPO_DIR"` 语法