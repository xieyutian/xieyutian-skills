# Fork一个仓库

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/forks`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(企业、组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| organization | string | 否 | 组织空间完整地址，不填写默认Fork到用户个人空间地址 |
| name | string | 否 | fork 后仓库名称。默认: 源仓库名称 |
| path | string | 否 | fork 后仓库地址。默认: 源仓库地址 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "organization": "string",

  "name": "string",

  "path": "string"

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("POST", "/api/v5/repos/:owner/:repo/forks", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```