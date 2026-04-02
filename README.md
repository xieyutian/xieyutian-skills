# xieyutian-skills

Claude Code 技能集合，包含多个用于提升开发效率的自动化技能。

## 技能列表

| 技能名称 | 描述 |
|---------|------|
| [gitcode-pr-review](#gitcode-pr-review) | GitCode Pull Request 代码审查技能 |
| [gitcode-api-helper](#gitcode-api-helper) | GitCode API 查询和检索技能 |

---

## gitcode-api-helper

提供 GitCode 平台 API 的查询、检索和说明服务。帮助用户快速找到所需的 API 文档，了解 API 的使用方法、参数说明和代码示例。

### 功能特点

- 按关键词检索 API 文档
- 按 API 端点精确查找
- 按功能分类浏览
- 提供详细的参数说明和代码示例
- 支持其他技能调用获取结构化 API 信息

### API 文档分类

| 分类 | 文档数 | 描述 |
|------|--------|------|
| OpenAPI 入门 | 1 | OpenAPI 使用入门和认证说明 |
| 仓库 | 35 | 仓库相关 API |
| 分支 | 8 | 分支相关 API |
| Issue | 27 | Issue 相关 API |
| Pull Request | 44 | PR 相关 API |
| 搜索 | 3 | 搜索相关 API |
| 用户 | 22 | 用户相关 API |
| 组织 | 18 | 组织相关 API |
| 企业 | 15 | 企业相关 API |
| Webhook | 6 | Webhook 相关 API |
| 更多... | - | 标签、里程碑、提交、发布等 |

### 使用方法

直接询问 GitCode API 相关问题：

```
如何创建一个 Pull Request？
获取仓库列表的 API 是什么？
GitCode 的 Webhook 如何配置？
```

### 目录结构

```
skills/gitcode-api-helper/
├── SKILL.md              # 技能定义和流程说明
├── scripts/
│   └── generate-index.py # 文档索引生成脚本
└── references/
    ├── index.json        # API 文档索引
    └── api-docs/         # API 文档目录
        ├── openapi-intro/
        ├── repositories/
        ├── pull-requests/
        ├── issues/
        └── ...
```

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
│   └── pr-comment.py     # 评论发布脚本（支持行号范围格式）
└── references/
    ├── checklists.md       # 完整审查清单
    ├── comment-format.md   # 行级评论格式规范
    ├── report-template.md  # 审查报告模板
    └── examples.md         # 使用示例
```

### 审查清单参考

详细审查清单请参阅 [checklists.md](skills/gitcode-pr-review/references/checklists.md)，包含：
- 修改全面性和正确性审查
- 安全审查（P0-P2 优先级分级）
- 代码质量审查

### 行级评论格式

行级评论格式规范请参阅 [comment-format.md](skills/gitcode-pr-review/references/comment-format.md)，关键要点：
- 代码块格式：` ```语言:文件路径#L行号`
- 支持行号范围：`#L34-35` 或 `#L34-L35`（自动取首行号发布）
- 只能引用实际存在的代码，严禁虚构

---

## License

MIT License