# 获取项目Pull Request列表

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls`

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
| state | string | 否 | 可选。Pull Request状态: all、open、closed、locked、merged，默认：all |
| base | string | 否 | 可选。Pull Request提交目标分支的名称 |
| since | string | 否 | 可选。起始的更新时间，要求时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| direction | string | 否 | 可选。升序/降序 默认：desc(asc 或者 desc) |
| sort | string | 否 | 可选。排序字段: created、updated 默认：created |
| milestone_number | integer | 否 | 可选。里程碑序号(id) |
| labels | string | 否 | 以逗号分隔的标签名称列表 |
| page | integer | 否 | 当前的页码:默认为 1 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |
| author | string | 否 | 可选。PR 创建者用户名 |
| assignee | string | 否 | 可选。PR 负责人用户名 |
| reviewer | string | 否 | 可选。PR 评审人用户名 |
| merged_after | string | 否 | 返回在指定时间之后合并的合并请求,要求时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| merged_before | string | 否 | 返回在指定时间之前合并的合并请求,要求时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| only_count | boolean | 否 | 如果为true，则仅返回合并请求的计数，默认为 false |
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

conn.request("GET", "/api/v5/repos/:owner/:repo/pulls", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```