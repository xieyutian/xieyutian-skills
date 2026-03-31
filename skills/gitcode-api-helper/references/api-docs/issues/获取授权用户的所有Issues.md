# 获取授权用户的所有Issues

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/user/issues`

## Request

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| filter | string | 否 | 筛选参数: 授权用户负责的(assigned)，授权用户创建的(created)，包含前两者的(all)。默认: assigned |
| state | string | 否 | Issue的状态: open（开启的）, progressing(进行中), closed（关闭的）, rejected（拒绝的）。默认: open |
| labels | string | 否 | 用逗号分开的标签。如: bug,performance |
| sort | string | 否 | 排序依据: 创建时间(created)，更新时间(updated_at)。默认: created_at |
| direction | string | 否 | 排序方式: 升序(asc)，降序(desc)。默认: desc |
| since | string | 否 | 起始的更新时间，要求时间格式为 ISO 8601 |
| page | integer | 否 | 当前的页码 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |
| schedule | string | 否 | 计划开始日期，格式：20181006T173008+80-20181007T173008+80（区间），或者 -20181007T173008+80（小于20181007T173008+80），或者 20181006T173008+80-（大于20181006T173008+80），要求时间格式为20181006T173008+80 |
| deadline | string | 否 | 计划截止日期，格式同上 |
| created_at | string | 否 | 任务创建时间，格式同上 |
| finished_at | string | 否 | 任务完成时间，即任务最后一次转为已完成状态的时间点。格式同上 |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/user/issues", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```