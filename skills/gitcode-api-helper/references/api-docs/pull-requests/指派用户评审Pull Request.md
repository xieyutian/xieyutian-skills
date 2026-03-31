# 指派用户评审Pull Request

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/reviewers`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(企业、组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| number | string | 是 | 第几个PR，即本仓库PR的序数。对应iid |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| reviewers | string | 是 | 用户的个人空间地址, 以逗号分隔 |
| add | boolean | 否 | 是否新增评审人，为true会新增评审人，false会覆盖更新评审人，默认false |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "reviewers": "string",

  "add": True

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("POST", "/api/v5/repos/:owner/:repo/pulls/:number/reviewers", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```