# 搜索 Issues

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/search/issues`

## Request

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| page | integer | 否 | 当前的页码 最大为 100 |
| per_page | integer | 否 | 每页的数量，最大为 50 |
| q | string | 是 | 搜索关键字 |
| sort | string | 否 | 排序字段，created_at(创建时间)、last_push_at(更新时间)，默认为最佳匹配 |
| order | string | 否 | 排序顺序 (默认:desc) |
| repo | string | 否 | 仓库路径 |
| state | string | 否 | 筛选指定状态的 issues, open(开启)、closed(完成) |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/search/issues", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```