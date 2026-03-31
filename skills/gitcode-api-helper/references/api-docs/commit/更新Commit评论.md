# 更新Commit评论

## API 端点

**方法:** `PATCH`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/comments/:id`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| id | string | 是 | 评论id |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| body | string | 是 | 评论内容 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "body": "string"

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PATCH", "/api/v5/repos/:owner/:repo/comments/:id", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```