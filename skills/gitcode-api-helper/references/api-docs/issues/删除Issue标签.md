# 删除Issue标签

## API 端点

**方法:** `DELETE`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/labels/:name`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| number | string | 是 | 第几个Issue，即本仓库Issue的序数 |
| name | string | 是 | 标签名称(批量删除用英文逗号分隔，如: bug,feature) |

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

conn.request("DELETE", "/api/v5/repos/:owner/:repo/issues/:number/labels/:name", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```