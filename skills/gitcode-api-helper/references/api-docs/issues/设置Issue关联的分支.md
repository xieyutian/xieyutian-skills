# 设置Issue关联的分支

## API 端点

**方法:** `PUT`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/related_branches`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| number | string | 是 | issue编号 |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "branch_names": [

    "string"

  ]

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PUT", "/api/v5/repos/:owner/:repo/issues/:number/related_branches", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```