# 修改项目保护 tag

## API 端点

**方法:** `PUT`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/protected_tags`

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
| name | string | 是 | 标签名称 |
| create_access_level | integer | 是 | 允许创建的访问级别(0:不允许任何人;30:开发者、维护者、管理员;40:维护者、管理员) |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "name": "string",

  "create_access_level": 0

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PUT", "/api/v5/repos/:owner/:repo/protected_tags", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```