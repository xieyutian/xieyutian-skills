# 获取 issue 关联的 pull requests

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/pull_requests`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(企业、组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| number | string | 是 | Issue 编号(区分大小写，无需添加 # 号) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| mode | integer | 否 | 1 (增强模式，传上述参数，返回 pr 的 mergeable 状态）; 0(默认，不返回mergeable 状态) |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/repos/:owner/:repo/issues/:number/pull_requests", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```