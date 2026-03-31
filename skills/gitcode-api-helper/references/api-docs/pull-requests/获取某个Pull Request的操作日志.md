# 获取某个Pull Request的操作日志

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/operate_logs`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| number | string | 是 |  |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| sort | string | 否 | 按递减(desc)排序，默认：递减 |
| page | integer | 否 | 当前的页码:默认为 1 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/repos/:owner/:repo/pulls/:number/operate_logs", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```