# 添加Issue或者Pull Request到看板

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v5/org/:owner/kanban/:kanban_id/add_item`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 组织的路径 |
| kanban_id | string | 是 | 看板id |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 否 | 用户授权码 |
| repo | string | 是 | 仓库的路径 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "repo": "string",

  "issue_iids": [

    0

  ],

  "pr_iids": [

    0

  ]

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("POST", "/api/v5/org/:owner/kanban/:kanban_id/add_item", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```