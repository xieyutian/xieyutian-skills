# 创建Pull Request

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| title | string | 是 | 必填。Pull Request标题 |
| head | string | 是 | 必填。Pull Request提交的源分支。格式：branch 如果跨仓PR传：username:branch |
| base | string | 是 | 必填。Pull Request提交目标分支的名称 |
| body | string | 否 | 可选。Pull Request内容 |
| milestone_number | integer | 否 | 可选。里程碑序号(id) |
| labels | string | 否 | 用逗号分开的标签，名称要求长度在 2-20 之间且非特殊字符。如: bug,performance |
| issue | string | 否 | 可选。Pull Request的标题和内容可以根据指定的Issue Id自动填充 |
| assignees | string | 否 | 可选。审查人员username，可多个，半角逗号分隔，如：(username1,username2), 注意: 当仓库代码审查设置中已设置【指派审查人员】则此选项无效 |
| testers | string | 否 | 可选。测试人员username，可多个，半角逗号分隔，如：(username1,username2), 注意: 当仓库代码审查设置中已设置【指派测试人员】则此选项无效 |
| prune_source_branch | boolean | 否 | 可选。合并PR后是否删除源分支，默认false（不删除） |
| draft | boolean | 否 | 是否设置为草稿 默认false |
| squash | boolean | 否 | 接受 Pull Request时使用扁平化（Squash）合并, 默认false |
| squash_commit_message | string | 否 | squash提交信息 |
| fork_path | string | 否 | fork项目路径【owner/repo】，跨仓PR 必填。 |
| close_related_issue | boolean | 否 | 可选，合并后是否关闭关联的 Issue，默认根据仓库配置设置 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "title": "string",

  "head": "string",

  "base": "string",

  "body": "string",

  "milestone_number": 0,

  "labels": "string",

  "issue": "string",

  "assignees": "string",

  "testers": "string",

  "prune_source_branch": True,

  "draft": True,

  "squash": True,

  "squash_commit_message": "string",

  "fork_path": "string",

  "close_related_issue": True

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("POST", "/api/v5/repos/:owner/:repo/pulls", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```