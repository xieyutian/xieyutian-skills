# xieyutian-skills

Claude Code 技能集合，包含多个用于提升开发效率的自动化技能。

## 技能列表

| 技能名称 | 描述 |
|---------|------|
| [gitcode-pr-review](#gitcode-pr-review) | GitCode Pull Request 自动批量审查技能 |

---

## gitcode-pr-review

自动扫描 GitCode 平台上 Cangjie 组织的两个核心仓库，批量审查最新开启的 Pull Request，跳过已审查的，对未审查的 PR 执行深度代码审查并发表评论。

### 固定审查范围

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

### 功能特点

- 自动扫描两个固定仓库的最新 PR
- 自动跳过已审查的 PR（通过用户评论判断）
- 基于完整文件内容的深度代码审查
- 安全审查清单（硬编码密钥、加密安全、输入验证等）
- 代码质量审查（逻辑错误、性能问题、命名规范等）
- 修改全面性评估（对照 PR 描述验证实现完整性）
- 自动发布行级评论到 GitCode PR
- 本地仓库缓存机制（避免重复克隆）

### 使用前提

- 系统已安装 Git
- 系统已安装 Python3 和 requests 库
- 有足够的磁盘空间克隆仓库
- **已配置 GitCode Token**（用于自动获取 PR 列表、检查审查状态、发布评论）

### 使用方法

直接触发技能即可自动开始批量审查：

```
/gitcode-pr-review
```

技能会自动：
1. 扫描两个仓库的最新 10 个 open PR
2. 跳过已审查的 PR
3. 对未审查的 PR 执行深度代码审查
4. 自动发布审查评论到 GitCode

### 输入参数

| 参数 | 说明 | 必填 |
|------|------|------|
| GitCode Token | GitCode 个人访问令牌（用于获取 PR 列表、检查审查状态、发布评论） | 是 |
| 本地仓库路径 | 用户已有的仓库目录路径（可选，用于覆盖缓存） | 否 |

> **重要变更**：仓库地址和 PR 编号**不再需要用户提供**，由技能自动从固定两个仓库获取最新 PR。

### 审查内容

#### 修改全面性和正确性
- PR 描述对照检查
- 问题定位准确性
- 修改完整性
- 测试覆盖

#### 安全审查
- 硬编码密钥检测
- 加密安全检查
- 输入验证
- 文件操作安全
- 网络请求安全
- 日志输出安全
- 权限控制

#### 代码质量审查
- 逻辑错误
- 性能问题
- 命名规范
- 代码结构
- 可读性
- 重复代码
- 错误处理

### 缓存机制

技能会自动记录仓库与本地目录的对应关系，存储在 `~/.gitcode-pr-review/repo_cache.json`。

下次审查相同仓库的 PR 时，自动使用缓存的本地目录，无需重复询问。

### 目录结构

```
skills/gitcode-pr-review/
├── SKILL.md              # 技能定义和流程说明
├── scripts/
│   ├── get_pr_info.py    # PR 信息获取脚本
│   └── pr-comment.py     # 评论发布脚本
└── references/
    ├── report-template.md # 审查报告模板
    └── examples.md       # 使用示例
```

## License

MIT License