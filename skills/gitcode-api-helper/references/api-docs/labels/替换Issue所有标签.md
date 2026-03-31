# 替换Issue所有标签

## API 端点

**方法:** `PUT`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/labels`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址（企业、组织或个人的地址path） |
| repo | string | 是 | 仓库路径(path) |
| number | string | 是 | Issue 编号(区分大小写，无需添加 # 号) |

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

payload = json.dumps([

  "string"

])

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PUT", "/api/v5/repos/:owner/:repo/issues/:number/labels", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```