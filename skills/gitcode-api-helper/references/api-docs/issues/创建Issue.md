# 创建Issue

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/issues`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| repo | string | 是 | 仓库路径 |
| title | string | 是 | Issue标题 |
| body | string | 是 | Issue描述 |
| assignee | string | 否 | Issue负责人的username，多个用英文逗号隔开 |
| milestone | integer | 否 | 里程碑序号 |
| labels | string | 否 | 用逗号分开的标签，名称要求长度在 2-20 之间且非特殊字符。如: bug,performance |
| security_hole | string | 否 | 是否是私有issue(默认为false) |
| template_path | string | 否 | issue模板路径，项目模板支持.gitcode，.github，.gitee目录下的文件，组织模板仅支持.gitcode项目下的.gitcode目录下的文件 |
| issue_type | string | 否 | issue类型（企业版支持），设置值需与企业issue高级功能中的设置保持一致 |
| issue_severity | string | 否 | issue优先级（企业版支持），设置值需与企业issue高级功能中的设置保持一致 |


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

  "assignee": "string",

  "milestone": 0,

  "labels": "string",

  "security_hole": "string",

  "template_path": "string",

  "issue_type": "string",

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

conn.request("POST", "/api/v5/repos/:owner/issues", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```