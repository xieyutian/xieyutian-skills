# 组织 Pull Request列表

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/org/:org/pull_requests`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| org | string | 是 | org(path/login) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| state | string | 否 | 可选。Pull Request状态，all，所有，open：开启，closed：关闭，merged：合并 |
| sort | string | 否 | 可选。排序字段，创建时间：created，更新时间：updated。默认按创建时间 |
| direction | string | 否 | 可选。升序：asc，降序：desc |
| page | integer | 否 | 当前的页码:默认为 1 |
| per_page | string | 否 | 每页数量:默认20 |
| base | string | 否 | 目标分支 |
| author | string | 否 | pull request作者 |
| search | string | 否 | 根据 title、description 模糊查询 |
| created_after | string | 否 | 返回在指定时间之后创建的合并请求,要求时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| created_before | string | 否 | 返回在指定时间之前创建的合并请求,要求时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| updated_before | string | 否 | 返回在指定时间之前更新的合并请求,要求时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| updated_after | string | 否 | 返回在指定时间之后更新的合并请求,要求时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/org/:org/pull_requests", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```