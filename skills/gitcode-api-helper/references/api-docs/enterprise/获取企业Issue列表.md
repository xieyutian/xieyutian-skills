# 获取企业Issue列表

## API 端点

**方法:** `POST`
**端点:** `https://api.gitcode.com/api/v8/enterprises/:enterprise_id/issues`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| enterprise_id | string | 是 | 企业id |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| page | integer | 否 | 当前的页码:默认为 1 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |
| labels | string | 否 | 标签，多个按英文逗号隔开 |
| sort | string | 否 | 排序依据: 创建时间(created)，更新时间(updated_at)。默认: created_at |
| direction | string | 否 | 排序方式: 升序(asc)，降序(desc)。默认: desc |
| since | string | 否 | 起始的更新时间，要求时间格式为 ISO 8601 |
| create_at | string | 否 | 任务创建日期，格式2024-11-09 |
| created_before | string | 否 | 任务创建截止时间，格式2024-11-09 |
| search | string | 否 | 通过关键字搜索issue标题 |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "page": 0,

  "per_page": 0,

  "labels": "string",

  "sort": "string",

  "direction": "string",

  "since": "string",

  "assignees": [

    "string"

  ],

  "milestone_ids": [

    0

  ],

  "project_ids": [

    0

  ],

  "create_at": "string",

  "created_before": "string",

  "search": "string",

  "issue_types": [

    "string"

  ],

  "issue_states": [

    "string"

  ],

  "custom_fields": [

    {

      "field_name": "string",

      "values": [

        "string"

      ],

      "operation": "string"

    }

  ]

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("POST", "/api/v8/enterprises/:enterprise_id/issues", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```