# 获取文件Blob

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/git/blobs/:sha`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| sha | string | 是 | 文件的 Blob SHA，可通过 [获取仓库具体路径下的内容] API 获取 |

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

conn.request("GET", "/api/v5/repos/:owner/:repo/git/blobs/:sha", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```