# 创建一个仓库的WebHooks

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/hooks`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址（企业、组织或个人的地址path） |
| repo | string | 是 | 仓库路径(path) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| url | string | 是 | 远程HTTP URL |
| encryption_type | integer | 否 | 加密类型: 0: 密码, 1: 签名密钥 |
| password | string | 否 | 请求URL时会带上该密码，防止URL被恶意请求 |
| push_events | boolean | 否 | Push代码到仓库 |
| tag_push_events | boolean | 否 | 提交Tag到仓库 |
| issues_events | boolean | 否 | 创建/关闭Issue |
| note_events | boolean | 否 | 评论了Issue/代码等等 |
| merge_requests_events | boolean | 否 | 合并请求和合并后 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "url": "string",

  "encryption_type": 0,

  "password": "string",

  "push_events": True,

  "tag_push_events": True,

  "issues_events": True,

  "note_events": True,

  "merge_requests_events": True

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("POST", "/api/v5/repos/:owner/:repo/hooks", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```