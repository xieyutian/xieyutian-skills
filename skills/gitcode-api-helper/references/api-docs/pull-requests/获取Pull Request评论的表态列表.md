# 获取Pull Request评论的表态列表

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/comment/:comment_id/user_reactions`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(企业、组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |
| comment_id | string | 是 | 评论的id |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| page | string | 否 | 当前页码 |
| per_page | string | 否 | 每页数量 |
| emoji_name | string | 否 | emoji表情，可选：like，dislike，smile，confused，love，rocket，eyes，party |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/api/v5/repos/:owner/:repo/pulls/comment/:comment_id/user_reactions", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```