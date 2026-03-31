# 重置 Pull Request测试 的状态

## API 端点

**方法:** `PATCH`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/testers`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| number | integer | 是 | 第几个PR，即本仓库PR的序数 |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| reset_all | boolean | 否 | 是否重置所有测试人，默认：false，只对管理员生效 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "reset_all": True

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PATCH", "/api/v5/repos/:owner/:repo/pulls/:number/testers", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```