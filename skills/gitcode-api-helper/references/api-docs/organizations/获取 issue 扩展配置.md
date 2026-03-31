# 获取 issue 扩展配置

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/orgs/:org/issue/extend/settings`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| org | string | 是 | 仓库所属空间地址(企业、组织 path) |

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

conn.request("GET", "/api/v5/orgs/:org/issue/extend/settings", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```