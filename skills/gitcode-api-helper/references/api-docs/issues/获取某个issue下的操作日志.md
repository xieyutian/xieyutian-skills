# 获取某个issue下的操作日志

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/issues/:number/operate_logs`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| number | string | 是 | issue编号 |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| repo | string | 是 | 仓库路径(path) |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/repos/:owner/issues/:number/operate_logs", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```