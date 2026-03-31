# 获取企业 issue 关联的 Pull Requests

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/enterprises/:enterprise/issues/:number/pull_requests`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| enterprise | string | 是 | org(path/login) |
| number | integer | 是 | issue 全局 id |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/enterprises/:enterprise/issues/:number/pull_requests", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```