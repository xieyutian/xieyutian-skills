# 测试WebHook是否发送成功

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/hooks/:id/tests`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址（企业、组织或个人的地址path） |
| repo | string | 是 | 仓库路径(path) |
| id | string | 是 | Webhook的ID |

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

conn.request("POST", "/api/v5/repos/:owner/:repo/hooks/:id/tests", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```