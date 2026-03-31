# 获取企业某个Issue所有评论

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/enterprises/:enterprise/issues/:number/comments`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| enterprise | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| number | integer | 是 | issue 全局唯一 id |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| page | integer | 否 | 当前的页码 |
| per_page | integer | 否 | 每页的数量：最大为 100，默认 20 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/enterprises/:enterprise/issues/:number/comments", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```