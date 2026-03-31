# 获取仓库某个Issue所有的评论

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/comments`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(企业、组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| number | string | 是 | Issue 编号(区分大小写，无需添加 # 号) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| page | integer | 否 | 当前的页码 |
| per_page | integer | 否 | 每页的数量，最大为 100，默认 20 |
| order | string | 否 | 排序顺序: asc(default),desc |
| since | string | 否 | 起始的更新时间，要求时间格式为 2024-11-10T08:10:30.000+08:00（注意+号要url编码为%2B） |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/repos/:owner/:repo/issues/:number/comments", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```