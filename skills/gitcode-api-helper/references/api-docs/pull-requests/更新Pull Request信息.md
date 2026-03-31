# 更新Pull Request信息

## API 端点

**方法:** `PATCH`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| number | integer | 是 | 第几个PR，即本仓库PR的序数 |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| title | string | 否 | 可选。Pull Request标题 |
| body | string | 否 | 可选。Pull Request内容 |
| state | string | 否 | 可选。Pull Request状态 |
| milestone_number | integer | 否 | 可选。里程碑序号(id) |
| labels | string | 否 | 用逗号分开的标签，名称要求长度在 2-20 之间且非特殊字符。如: bug,performance |
| draft | boolean | 否 | 是否设置为草稿 |
| close_related_issue | boolean | 否 | 可选，合并后是否关闭关联的 Issue，默认根据仓库配置设置 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "title": "string",

  "body": "string",

  "state": "string",

  "milestone_number": 0,

  "labels": "string",

  "draft": True,

  "close_related_issue": True

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PATCH", "/api/v5/repos/:owner/:repo/pulls/:number", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```