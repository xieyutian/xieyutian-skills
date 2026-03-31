# 获取或刷新授权 Token 接口

## Request

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| grant_type | string | 是 | 授权码模式 |
| code | string | 否 | 授权码 |
| client_id | string | 否 | 注册的客户端 ID |
| client_secret | string | 否 | 注册的客户端密钥 |
| refresh_token | string | 否 | 刷新令牌，仅在 grant_type 为 refresh_token 时必传 |
| client_secret | string | 是 | 注册的客户端密钥 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("gitcode.com")

payload = json.dumps({

  "client_secret": "string"

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("POST", "/oauth/token", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```