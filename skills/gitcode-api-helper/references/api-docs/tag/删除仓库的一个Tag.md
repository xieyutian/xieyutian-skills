# 删除仓库的一个Tag

## API 端点

**方法:** `DELETE`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/tags/:tag_name`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| tag_name | string | 是 | tag名称 |

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

  'Accept': '*/*'

}

conn.request("DELETE", "/api/v5/repos/:owner/:repo/tags/:tag_name", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```