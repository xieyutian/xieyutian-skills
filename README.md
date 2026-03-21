# xieyutian-skills

Claude Code 技能集合，包含多个用于提升开发效率的自动化技能。

## 技能列表

| 技能名称 | 描述 |
|---------|------|
| [gitcode-pr-review](#gitcode-pr-review) | GitCode Pull Request 代码审查技能 |

---

## gitcode-pr-review

对 GitCode 平台的 Pull Request 进行自动化代码审查，识别潜在问题、安全漏洞并提供改进建议。

### 功能特点

- 自动获取 PR 信息和文件变更
- 基于完整文件内容的深度代码审查
- 安全审查清单（硬编码密钥、加密安全、输入验证等）
- 代码质量审查（逻辑错误、性能问题、命名规范等）
- 修改全面性评估（对照 PR 描述验证实现完整性）
- 自动发布行级评论到 GitCode PR

### 使用前提

- 系统已安装 Git
- 系统已安装 Python3 和 requests 库
- 有足够的磁盘空间克隆仓库
- 已配置 GitCode Token（用于发布评论）

### 使用方法

当需要审查 GitCode 仓库的 PR 时，提供仓库 Clone 地址和 PR 编号即可触发技能：

```
请帮我审查这个 PR: https://gitcode.com/owner/repo/pulls/123
```

或直接提供信息：
```
请审查 GitCode 仓库 https://gitcode.com/owner/repo.git 的 PR #123
```

### 输入参数

| 参数 | 说明 | 必填 |
|------|------|------|
| 仓库 Clone 地址 | GitCode 仓库的 HTTPS 或 SSH 克隆地址 | 是* |
| PR 编号 | 要审查的 Pull Request 编号 | 是 |
| GitCode Token | GitCode 个人访问令牌 | 是 |
| 本地仓库路径 | 已有的仓库目录路径 | 否 |

> 如果提供了本地仓库路径，则 Clone 地址可从本地仓库获取。

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

---

## License

MIT License