# 更新Issue或者Pull Request关联的看板

## API 端点

**方法:** `PUT`
**端点:** `https://api.gitcode.com/api/v5/org/:owner/kanban/repo/:repo/:type/:iid`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 组织的路径 |
| repo | string | 是 | 仓库的路径 |
| type | string | 是 | 类型，issue/merge_request |
| iid | string | 是 | issue或者pull request的iid |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 否 | 用户授权码 |
| kanban_id | string | 是 | 看板id |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "kanban_id": "string"

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PUT", "/api/v5/org/:owner/kanban/repo/:repo/:type/:iid", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```