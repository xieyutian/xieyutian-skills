# 列出授权用户的Pull Request列表

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/user/pulls`

## Request

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| state | string | 否 | 返回已打开、已关闭、已锁定、已合并或所有合并请求， open：已打开；closed：已关闭；locked：已锁定；merged：已合并；all：所有。默认返回所有的 |
| sort | string | 否 | 返回按字段排序的合并请求，创建时间：created；更新时间：updated；合并时间：merged_at。默认按照创建时间排序 |
| direction | string | 否 | 返回按照排序字段升序或者降序的合并请求，desc：降序；asc：升序 |
| labels | string | 否 | 逗号分隔的标签名称 |
| created_after | string | 否 | 返回在指定时间之后创建的合并请求，时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| created_before | string | 否 | 返回在指定时间之前创建的合并请求，时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| updated_after | string | 否 | 返回在指定时间之后更新的合并请求，时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| updated_before | string | 否 | 返回在指定时间之前更新的合并请求，时间格式为 ISO 8601 例如：2024-11-20T13:00:21+08:00 |
| scope | string | 否 | 返回给定范围的合并请求，need_my_approve：需要我审查的；created_by_me：由我创建的；assigned_to_me：分配给我的；need_my_review：需要我评审的。默认返回我创建的 |
| source_branch | string | 否 | 返回具有给定源分支的合并请求 |
| target_branch | string | 否 | 返回具有给定目标分支的合并请求 |
| per_page | string | 否 | 每页的数量，最大为 100，默认 20 |
| page | string | 否 | 当前的页码 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/user/pulls", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```