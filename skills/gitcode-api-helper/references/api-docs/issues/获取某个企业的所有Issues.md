# 获取某个企业的所有Issues

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/enterprises/:enterprise/issues`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| enterprise | string | 是 | 企业的路径(path/login) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| state | string | 否 | Issue的状态: open（开启的）, closed（关闭的）, all（所有） 默认: open |
| labels | string | 否 | 用逗号分开的标签。如: bug,performance |
| sort | string | 否 | 排序依据: 创建时间(created)，更新时间(updated_at)。默认: created_at |
| direction | string | 否 | 排序方式: 升序(asc)，降序(desc)。默认: desc |
| since | string | 否 | 起始的更新时间，要求时间格式为 ISO 8601 |
| page | integer | 否 | 当前的页码 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |
| milestone | string | 否 | 根据里程碑标题。none为没里程碑的，*为所有带里程碑的 |
| assignee | string | 否 | 用户的username。 none为没指派者, *为所有带有指派者的 |
| creator | string | 否 | 创建Issues的用户username |
| program | string | 否 | 所属项目名称。none为没所属有项目的，*为所有带所属项目的 |
| created_at | string | 否 | 任务创建日期，格式2024-11-09 |
| created_before | string | 否 | 任务创建截止时间，格式2024-11-09 |
| search | string | 否 | 通过关键字搜索issue标题或者内容 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/enterprises/:enterprise/issues", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```