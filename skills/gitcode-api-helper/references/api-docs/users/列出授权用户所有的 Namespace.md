# 列出授权用户所有的 Namespace

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/user/namespaces`

## Request

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| mode | string | 否 | 参与方式: project(所有参与仓库的namepsce)、intrant(所加入的namespace)、all(包含前两者)，默认(intrant) |
| page | integer | 否 | 当前页码 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/user/namespaces", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```