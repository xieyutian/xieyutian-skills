# 获取仓库所有 issues

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/issues`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| state | string | 否 | Issue的状态: open（开启的）, closed（关闭的）， all (所有)。 默认: all |
| labels | string | 否 | 用逗号分开的标签。如: bug,performance |
| sort | string | 否 | 排序依据: 创建时间(created)，更新时间(updated)。默认: created |
| direction | string | 否 | 排序方式: 升序(asc)，降序(desc)。默认: desc |
| since | string | 否 | 起始的更新时间，要求时间格式为 2024-11-10T08:10:30.000+08:00（注意+号要url编码为%2B） |
| page | integer | 否 | 当前的页码 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |
| created_at | string | 否 | 任务创建时间，例如：2024-11-20T13:00:21+08:00 |
| milestone | string | 否 | 根据里程碑标题。none为没里程碑的 |
| assignee | string | 否 | Issue指派人ID |
| creator | string | 否 | 创建Issues的用户username |
| created_after | string | 否 | 返回在指定时间之后创建的问题，例如：2024-11-20T13:00:21+08:00 |
| created_before | string | 否 | 返回在指定时间之前创建的问题，例如：2024-11-20T13:00:21+08:00 |
| updated_after | string | 否 | 返回在指定时间之后更新的问题，例如：2024-11-20T13:00:21+08:00 |
| updated_before | string | 否 | 返回在指定时间之前更新的问题，例如：2024-11-20T13:00:21+08:00 |
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

conn.request("GET", "/api/v5/repos/:owner/:repo/issues", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```