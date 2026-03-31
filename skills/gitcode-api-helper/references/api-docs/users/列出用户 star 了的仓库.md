# 列出用户 star 了的仓库

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/users/:username/starred`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| username | string | 是 |  |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 否 | 用户授权码 |
| sort | string | 否 | created/last_push 根据仓库创建时间(created)或最后推送时间(updated)进行排序，默认：创建时间 |
| direction | string | 否 | asc/desc 排序方向，默认：降序 |
| page | integer | 否 | 当前的页码 |
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

conn.request("GET", "/api/v5/users/:username/starred", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```