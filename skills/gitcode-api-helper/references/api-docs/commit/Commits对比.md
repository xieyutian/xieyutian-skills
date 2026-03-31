# Commits对比

## API 端点

**方法:** `GET`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/compare/:base...:head`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址（企业、组织或个人的地址path） |
| repo | string | 是 | 仓库路径(path) |
| base | string | 是 | 对比的起点。Commit SHA、分支名或标签名 |
| head | string | 是 | 对比的终点。Commit SHA、分支名或标签名 |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| straight | boolean | 否 | 是否直对比。默认 false |
| suffix | string | 否 | 按照文件后缀过滤文件，如 .txt。只影响 files |


## 代码示例

### Python

```python
import http.client



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = ''

headers = {

  'Accept': 'application/json'

}

conn.request("GET", "/", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```