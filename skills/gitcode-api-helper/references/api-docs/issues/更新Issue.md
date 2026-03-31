# 更新Issue

## API 端点

**方法:** `PATCH`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/issues/:number`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| number | string | 是 | 第几个 issue，即本仓库 issue 的序数 |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| repo | string | 是 | 仓库路径 |
| title | string | 是 | Issue标题 |
| body | string | 否 | Issue描述 |
| state | string | 否 | Issue 状态，reopen（开启的）、close（关闭的） |
| assignee | string | 否 | Issue负责人的username，多个用英文逗号隔开 |
| milestone | integer | 否 | 里程碑序号 |
| labels | string | 否 | 用逗号分开的标签，名称要求长度在 2-20 之间且非特殊字符。如: bug,performance |
| security_hole | string | 否 | 是否是私有issue(默认为false) |
| status | string | 否 | issue状态（企业版支持） |
| issue_severity | string | 是 | issue优先级（企业版支持） |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "repo": "string",

  "title": "string",

  "body": "string",

  "state": "string",

  "assignee": "string",

  "milestone": 0,

  "labels": "string",

  "security_hole": "string",

  "status": "string",

  "issue_severity": "string",

  "custom_fields": [

    {

      "field_name": "string",

      "field_values": [

        "string"

      ]

    }

  ]

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PATCH", "/api/v5/repos/:owner/issues/:number", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```