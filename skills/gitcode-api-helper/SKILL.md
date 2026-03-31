---
name: gitcode-api-helper
description: GitCode API 帮助技能。当用户提到 GitCode API、需要查询 GitCode API 用法、参数说明、端点信息，或需要调用 GitCode 平台接口时，自动触发此技能。支持按关键词、API 端点、功能分类检索相关 API 文档，并提供详细的参数说明和代码示例。此技能也可被其他技能调用，用于获取 GitCode API 信息。
---

# GitCode API Helper

提供 GitCode 平台 API 的查询、检索和说明服务。帮助用户快速找到所需的 API 文档，了解 API 的使用方法、参数说明和代码示例。

## 使用前提

- 已有 GitCode 账户（如需实际调用 API）
- 已获取 GitCode access_token（如需实际调用 API）
- 网络连接正常（如需联网搜索额外信息）

## 输入参数

| 参数 | 说明 | 必填 | 示例 |
|------|------|------|------|
| 用户问题 | 用户关于 GitCode API 的问题或需求 | 是 | "如何创建一个 Pull Request？" |
| 检索关键词 | 用于检索 API 文档的关键词（可从用户问题中提取） | 否 | "创建", "Pull Request", "PR" |
| API 分类 | 指定 API 分类（如 repositories、issues、pull-requests） | 否 | "pull-requests" |
| API 端点 | 已知的 API 端点（方法 + 路径） | 否 | "POST /repos/:owner/:repo/pulls" |
| 调用来源 | 标识是否被其他技能调用 | 否 | "gitcode-pr-review" |

## 流程变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `USER_QUESTION` | 用户的原始问题 | "如何创建一个 Pull Request？" |
| `EXTRACTED_KEYWORDS` | 从问题中提取的关键词 | ["创建", "Pull Request", "PR"] |
| `MATCHED_DOCS` | 匹配到的文档列表 | `[{"id": "pr-create", "name": "创建Pull Request"}]` |
| `SELECTED_DOC` | 用户选择或自动选择的文档 | `{"id": "pr-create", ...}` |
| `DOC_CONTENT` | 文档完整内容 | "..." |
| `ADDITIONAL_INFO_NEEDED` | 是否需要联网搜索补充信息 | `true` / `false` |

## API 文档检索流程

### 步骤 1: 理解用户问题

**目的**：分析用户问题，识别用户意图和需求。

**执行操作**：

1. **识别问题类型**：
   - API 使用咨询（"如何使用某个 API？"）
   - API 查找（"有没有可以 XXX 的 API？"）
   - 参数说明（"某个参数是什么意思？"）
   - 端点查询（"某个功能的 API 端点是什么？"）
   - 代码示例（"如何用 Python 调用某个 API？"）

2. **提取关键词**：
   - 从用户问题中提取关键词
   - 识别 API 分类（如 repositories、issues、pull-requests）
   - 识别 API 功能（如创建、更新、删除、获取）
   - 识别操作对象（如 Issue、PR、仓库、分支）

3. **确定检索策略**：
   - 如果问题明确指定了功能 → 直接检索对应 API
   - 如果问题比较模糊 → 按关键词检索多个相关 API
   - 如果问题涉及参数 → 检索对应 API 后定位到参数部分

---

### 步骤 2: 从索引检索相关文档

**目的**：从 `references/index.json` 中快速检索相关 API 文档。

**执行操作**：

1. **加载索引文件**：
   ```bash
   Read skills/gitcode-api-helper/references/index.json
   ```

2. **执行检索**：

   **方法 1：按关键词检索**（推荐）
   - 遍历所有文档的 `keywords` 字段
   - 匹配用户问题中的关键词
   - 计算匹配度得分
   - 返回匹配度最高的前 5 个文档

   **方法 2：按 API 端点检索**
   - 如果用户提供了 API 端点（如 "POST /repos/:owner/:repo/pulls"）
   - 直接在 `apiEndpoint` 字段中查找匹配项

   **方法 3：按分类浏览**
   - 如果用户指定了分类（如 "pull-requests"）
   - 返回该分类下的所有文档列表

3. **输出检索结果**：

   向用户展示匹配的文档列表：
   ```
   找到以下相关 API 文档：

   1. 创建Pull Request (匹配度: 95%)
      - 分类: pull-requests
      - API: POST /repos/:owner/:repo/pulls
      - 摘要: 创建一个新的 Pull Request

   2. 获取项目Pull Request列表 (匹配度: 60%)
      - 分类: pull-requests
      - API: GET /repos/:owner/:repo/pulls
      - 摘要: 获取项目的 Pull Request 列表
   ```

---

### 步骤 3: 读取所需文档

**目的**：读取用户选择或自动选择的文档内容。

**执行操作**：

1. **确定要读取的文档**：
   - 如果匹配结果只有 1 个 → 自动选择
   - 如果匹配结果有多个 → 询问用户选择，或自动选择匹配度最高的

2. **读取文档内容**：
   ```bash
   Read skills/gitcode-api-helper/<文档路径>
   ```

3. **解析文档结构**：
   - 提取 API 端点（方法 + URL）
   - 提取 PATH PARAMETERS
   - 提取 QUERY PARAMETERS
   - 提取代码示例

---

### 步骤 4: 回答用户问题

**目的**：根据文档内容回答用户问题，必要时联网搜索补充信息。

**执行操作**：

1. **基于文档内容回答**：
   - 提取与用户问题相关的信息
   - 组织成清晰的回答格式
   - 提供参数说明、示例代码等

2. **判断是否需要联网搜索**：

   **需要联网搜索的情况**：
   - 用户问题涉及 API 的最新变更或新增功能
   - 用户问题涉及文档中未说明的错误处理
   - 用户问题涉及最佳实践、常见问题等

   **不需要联网搜索的情况**：
   - 用户问题仅涉及 API 端点、参数说明
   - 用户问题仅需代码示例
   - 用户问题可从现有文档中完全解答

3. **联网搜索（如需要）**：
   ```bash
   WebSearch "GitCode API <关键词> best practices 2026"
   ```

4. **组织最终回答**：

   **回答格式**：

   ```markdown
   ## API 概述

   [简要说明 API 的功能]

   ## API 端点

   - **方法**: POST
   - **端点**: `https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls`

   ## 参数说明

   ### PATH PARAMETERS

   | 参数名 | 类型 | 必填 | 描述 |
   |--------|------|------|------|
   | owner | string | 是 | 仓库所属空间地址 |
   | repo | string | 是 | 仓库路径 |

   ### QUERY PARAMETERS

   | 参数名 | 类型 | 必填 | 描述 |
   |--------|------|------|------|
   | access_token | string | 是 | 用户授权码 |
   | title | string | 是 | Pull Request 标题 |
   ...

   ## 代码示例

   [从文档中提取的 Python 示例代码]

   ## 注意事项

   - [从文档中提取的注意事项]
   ```

---

### 步骤 5: 处理其他技能的调用（可选）

**目的**：当其他技能调用此技能时，提供结构化的 API 信息返回。

**执行操作**：

如果检测到 `调用来源` 参数（非空），执行以下流程：

1. **识别调用需求**：
   - 调用来源技能传递参数：`{"source": "gitcode-pr-review", "need": "API 端点信息", "api": "创建 Pull Request"}`
   - 识别需要返回的信息类型

2. **返回结构化数据**：

   不向用户展示交互式回答，而是直接返回结构化数据：

   ```json
   {
     "status": "success",
     "api": {
       "name": "创建Pull Request",
       "method": "POST",
       "endpoint": "https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls",
       "pathParameters": [...],
       "queryParameters": [...],
       "codeExample": {...}
     }
   }
   ```

3. **支持批量查询**：

   如果调用来源需要查询多个 API，返回数组格式的结果。

---

## API 分类索引

技能包含以下 API 分类，每个分类下有多个文档：

| 分类 | 名称 | 文档数 | 描述 |
|------|------|--------|------|
| openapi-intro | OpenAPI入门 | 1 | OpenAPI 使用入门和认证说明 |
| repositories | 仓库 | 35 | 仓库相关 API，包括创建、删除、获取仓库信息、文件操作等 |
| branch | 分支 | 8 | 分支相关 API，包括创建、删除、获取分支信息、保护分支等 |
| issues | Issue | 27 | Issue 相关 API，包括创建、更新、获取、评论 Issue 等 |
| pull-requests | Pull Request | 44 | PR 相关 API，包括创建、合并、获取、评论 PR 等 |
| search | 搜索 | 3 | 搜索相关 API，包括搜索仓库、用户、Issue 等 |
| users | 用户 | 22 | 用户相关 API，包括获取用户信息、更新资料、关注等 |
| organizations | 组织 | 18 | 组织相关 API，包括创建、管理组织等 |
| enterprise | 企业 | 15 | 企业相关 API，包括企业管理、统计等 |
| webhooks | Webhook | 6 | Webhook 相关 API，包括创建、管理 Webhook 等 |
| labels | 标签 | 9 | 标签相关 API，包括创建、更新、删除标签等 |
| milestone | 里程碑 | 5 | 里程碑相关 API，包括创建、更新、删除里程碑等 |
| member | 成员 | 6 | 成员相关 API，包括添加、删除成员等 |
| commit | 提交 | 12 | 提交相关 API，包括获取提交信息、比对提交等 |
| release | 发布 | 8 | 发布相关 API，包括创建、更新、删除发布版本等 |
| tag | Tag | 8 | 标签相关 API，包括创建、获取、删除标签等 |
| dashboard | 仪表盘 | 7 | 仪表盘相关 API，包括获取动态、通知等 |
| ai-hub | AI Hub | 7 | AI Hub 相关 API，包括文本生成、图像识别等 |
| oauth | OAuth | 1 | OAuth 2.0 相关 API，包括授权、获取 token 等 |
| changelog | 变更日志 | 16 | API 变更日志，记录 API 的更新历史 |

---

## 与其他技能的协作方式

### 被动调用模式

其他技能可以通过传递 `调用来源` 参数来调用此技能，获取结构化的 API 信息。

**调用示例**：

其他技能（如 gitcode-pr-review）在执行过程中需要查询 GitCode API 信息时，可以：
1. 检测到需要 GitCode API 信息
2. 调用 gitcode-api-helper 技能，传递参数：`调用来源: "gitcode-pr-review"`
3. gitcode-api-helper 执行检索流程，返回结构化数据
4. gitcode-pr-review 接收数据，继续执行后续流程

### 主动协助模式

当用户直接向此技能提问时，提供交互式的问答服务。

---

## 注意事项

- **优先使用本地文档**：优先从索引和文档中检索，避免不必要的联网搜索
- **匹配度阈值**：设置匹配度阈值（如 50%），低于阈值时询问用户是否继续
- **多文档选择**：当检索到多个相关文档时，展示列表供用户选择
- **参数完整性**：回答时务必说明哪些参数是必填的，哪些是可选的
- **代码示例**：优先提供 Python 示例
- **版本说明**：如用户问题涉及 API 版本差异，明确说明版本信息
- **错误处理**：提供常见错误码和错误处理建议（需从文档或联网搜索获取）
- **权限说明**：说明调用 API 所需的权限（如 access_token 的获取方式）
- **调用来源处理**：当检测到被其他技能调用时，不进行交互式询问，直接返回结构化数据
- **文档索引更新**：当 API 文档更新时，需要同步更新 `references/index.json`

---

## 常见问题处理

### Q1: 用户问题过于模糊

**用户问题**: "GitCode API 怎么用？"

**处理方式**:
1. 提供概述性回答，介绍 GitCode API 的基本使用方式
2. 列出常用的 API 分类
3. 询问用户具体想实现什么功能

### Q2: 检索结果过多或过少

**检索结果过多**（>10 个）:
1. 提示用户缩小搜索范围
2. 提供分类筛选选项

**检索结果过少**（=0 个）:
1. 询问用户是否需要联网搜索
2. 建议用户尝试其他关键词

### Q3: 用户需要实际调用 API

**用户需求**: "帮我调用创建 PR 的 API"

**处理方式**:
1. 提供 API 调用所需的参数列表
2. 询问用户必要的参数值
3. 询问用户是否已有 access_token
4. 如果用户没有 access_token，提供获取方式（链接到 OAuth 文档）
5. 生成完整的调用示例代码供用户参考