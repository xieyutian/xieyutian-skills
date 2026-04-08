# 使用示例

## 示例 1：首次创建发行版

**用户输入**：
> 帮我创建一个发行版

**执行流程**：

### 步骤 0: 解析本地仓库
```
$ git -C . remote -v
origin  https://gitcode.com/xieyutian/my-project.git (fetch)
origin  https://gitcode.com/xieyutian/my-project.git (push)

解析结果:
  Owner: xieyutian
  Repo: my-project
  当前分支: main

$ git fetch origin --tags
（同步远程分支和 Tags）
```

### 步骤 1: 获取版本历史
```bash
python scripts/create_release.py <token> xieyutian my-project --get-tags
# 输出: 暂无 Tag

python scripts/create_release.py <token> xieyutian my-project --get-latest-release
# 输出: 暂无 Release

$ git -C . log --oneline --no-merges -20
a1b2c3d feat: 添加用户注册功能
e4f5g6h feat: 实现文章发布模块
i7j8k9l fix: 修复登录页面样式问题
m0n1o2p docs: 更新 API 文档
q3r4s5t feat: 添加搜索功能
```

### 步骤 2: 推断版本号
```
分析结果:
- 无历史 Tag，建议首个版本号: v1.0.0
- Commit 分析:
  - feat: 3 个（新功能）
  - fix: 1 个（修复）
  - docs: 1 个（文档）

推荐版本号: v1.0.0
```

### 步骤 3: 生成描述、确认并创建
展示确认信息：
```
发行版创建确认:

Tag 名称: v1.0.0
发行版标题: v1.0.0 - 首个正式版本
目标分支: main
类型: 正式版

发行版描述:
  ## v1.0.0 - 首个正式版本

  发布日期: 2026-04-08

  ### ✨ 新功能

  - 添加用户注册功能
  - 实现文章发布模块
  - 添加搜索功能

  ### 🐛 修复

  - 修复登录页面样式问题

  ### 📦 其他变更

  - 更新 API 文档
```

用户确认后：
```bash
python scripts/create_release.py <token> xieyutian my-project \
  --create-release \
  --tag-name "v1.0.0" \
  --name "v1.0.0 - 首个正式版本" \
  --body-file /tmp/release_body.md \
  --target-commitish "main"
```

### 步骤 4: 验证
```
发行版创建成功！

Tag: v1.0.0
标题: v1.0.0 - 首个正式版本
链接: https://gitcode.com/xieyutian/my-project/releases/tag/v1.0.0
```

---

## 示例 2：版本升级

**用户输入**：
> 发布一个新版本，刚才合入了一些修复

**执行流程**：

### 步骤 0-1
```bash
$ git fetch origin --tags

python scripts/create_release.py <token> xieyutian my-project --get-tags
# 输出: v1.0.0 (commit: a1b2c3d4)

python scripts/create_release.py <token> xieyutian my-project --get-latest-release
# 输出: Tag: v1.0.0, 标题: v1.0.0 - 首个正式版本

$ git -C . log v1.0.0..HEAD --oneline --no-merges
b2c3d4e fix: 修复搜索结果排序错误
c3d4e5f fix: 修复文章列表分页问题
d4e5f6g feat: 添加文章标签功能
e5f6g7h refactor: 优化数据库查询
```

### 步骤 2: 推断版本号
```
当前最新 Tag: v1.0.0
分析结果:
- feat: 1 个 → 建议 minor 升级
- fix: 2 个
- refactor: 1 个

推荐版本号: v1.1.0（检测到新功能）
```

### 步骤 3-4: 同示例 1

---

## 示例 3：手动指定版本号

**用户输入**：
> 创建发行版，版本号用 v2.0.0

**执行流程**：

步骤 0-1 正常执行获取信息，但步骤 2 跳过自动推断，直接使用用户指定的 `v2.0.0`。

后续步骤与示例 1 相同。

---

## 示例 4：创建失败处理

**场景**：Tag 已存在导致 409 冲突

```
错误: HTTP 409 - 冲突：Tag 或 Release 已存在

处理建议：
- 远程已存在 v1.2.0 Tag，请选择：
  1. 更换版本号为 v1.2.1
  2. 删除远程 Tag 后重试: git push origin --delete v1.2.0
  3. 基于已有 Tag 重新创建 Release
```
