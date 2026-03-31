# 列出 star 了仓库的用户

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/stargazers`

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
| page | integer | 否 | 当前的页码 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |
| starred_after | string | 否 | 在此之后star的 |
| starred_before | string | 否 | 在此之前star的 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/repos/:owner/:repo/stargazers", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```