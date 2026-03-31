# 获取当前用户某个组织的Issues

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/orgs/:org/issues`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| org | string | 是 | 组织的路径(path/login) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| filter | string | 否 | 筛选参数：授权用户负责的(assigned)，授权用户创建的(created)，包含前两者的(all)。默认：assigned |
| state | string | 否 | Issue的状态：open（开启的）, closed（关闭的）,默认：open |
| labels | string | 否 | 用逗号分开的标签。如：bug,performance |
| sort | string | 否 | 排序依据：创建时间(created)，更新时间(updated_at)。默认：created_at |
| direction | string | 否 | 排序方式：升序(asc)，降序(desc)。默认：desc |
| page | integer | 否 | 当前的页码 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |
| created_at | string | 否 | 任务创建时间，格式同上 |
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

conn.request("GET", "/api/v5/orgs/:org/issues", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```