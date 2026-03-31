# 创建仓库Release

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/releases`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址（企业、组织或个人的地址path） |
| repo | string | 是 | 仓库路径 |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| tag_name | string | 是 | tag名称 |
| name | string | 是 | release名称 |
| body | string | 是 | release描述 |
| target_commitish | string | 否 | 分支名称或者commit SHA，如果tag不存在，需要新建tag则传入该参数，如果不传入该参数，则为默认分支的最新提交 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "tag_name": "string",

  "name": "string",

  "body": "string",

  "target_commitish": "string"

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("POST", "/api/v5/repos/:owner/:repo/releases", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```