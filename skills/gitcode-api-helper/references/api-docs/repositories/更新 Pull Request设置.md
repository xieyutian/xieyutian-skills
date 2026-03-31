# 更新 Pull Request设置

## API 端点

**方法:** `PUT`
**端点:** `https://api.gitcode.com/api/v5/repos/:owner/:repo/pull_request_settings`

## Request

### PATH PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| owner | string | 是 | 仓库所属空间地址(企业、组织或个人的地址path) |
| repo | string | 是 | 仓库路径(path) |

### QUERY PARAMETERS

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| access_token | string | 是 | 用户授权码 |
| approval_required_reviewers_enable | boolean | 否 | 是否启用审批必需的评审者功能 |
| approval_required_reviewers | integer | 否 | 需要的审批者数量(最小评审人数【选择的数字：1~5, 如果取消评审人功能传入0】) |
| only_allow_merge_if_all_discussions_are_resolved | boolean | 否 | 评审问题全部解决才能合入 |
| only_allow_merge_if_pipeline_succeeds | boolean | 否 | 是否仅在流水线成功后才允许合并 |
| disable_merge_by_self | boolean | 否 | 禁止合入自己创建的合并请求 |
| can_force_merge | boolean | 否 | 允许管理员强制合入 |
| add_notes_after_merged | boolean | 否 | 允许合并请求合并后继续做代码检视和评论 |
| mark_auto_merged_mr_as_closed | boolean | 否 | 是否将自动合并的MR状态标记为关闭状态 |
| can_reopen | boolean | 否 | 是否可以重新打开一个已经关闭的合并请求 |
| delete_source_branch_when_merged | boolean | 否 | 合并时是否删除源分支，默认删除原分支 |
| disable_squash_merge | boolean | 否 | 禁止 Squash 合并 |
| auto_squash_merge | boolean | 否 | 新建合并请求，默认开启 Squash 合并 |
| merge_method | string | 否 | 合并模式三选一(通过 merge commit 合并：merge；通过 merge commit 合并 （记录半线性历史）：rebase_merge；fast - forward 合并：ff) |
| squash_merge_with_no_merge_commit | boolean | 否 | Squash 合并不产生 Merge 节点 |
| merged_commit_author | string | 否 | 使用 MR (合入/创建) 者生成 Merge Commit（使用 PR 合入者生成 Merge Commit：传 merged_by; 使用 PR 创建者生成 Merge Commit：传 created_by） |
| approval_required_approvers | integer | 否 | 需要审批的批准者数量 |
| approval_approver_ids | string | 否 | 项目审查人, user_id 以逗号分隔 |
| approval_tester_ids | string | 否 | 项目测试人，user_id以逗号分隔 |
| approval_required_testers | integer | 否 | 测试最小通过人数 |
| is_check_cla | boolean | 否 | 是否校验CLA |
| is_allow_lite_merge_request | boolean | 否 | 是否启用轻量级 Pull Request |
| lite_merge_request_prefix_title | string | 否 | 轻量级 pr 的标题前缀 |
| close_issue_when_mr_merged | boolean | 否 | 创建 Pull Request时,默认选中 “合并后关闭已关联的 Issue” |


## 代码示例

### Python

```python
import http.client

import json



conn = http.client.HTTPSConnection("api.gitcode.com")

payload = json.dumps({

  "approval_required_reviewers_enable": True,

  "approval_required_reviewers": 0,

  "only_allow_merge_if_all_discussions_are_resolved": True,

  "only_allow_merge_if_pipeline_succeeds": True,

  "disable_merge_by_self": True,

  "can_force_merge": True,

  "add_notes_after_merged": True,

  "mark_auto_merged_mr_as_closed": True,

  "can_reopen": True,

  "delete_source_branch_when_merged": True,

  "disable_squash_merge": True,

  "auto_squash_merge": True,

  "merge_method": "string",

  "squash_merge_with_no_merge_commit": True,

  "merged_commit_author": "string",

  "approval_required_approvers": 0,

  "approval_approver_ids": "string",

  "approval_tester_ids": "string",

  "approval_required_testers": 0,

  "is_check_cla": True,

  "is_allow_lite_merge_request": True,

  "lite_merge_request_prefix_title": "string",

  "close_issue_when_mr_merged": True

})

headers = {

  'Content-Type': 'application/json',

  'Accept': 'application/json'

}

conn.request("PUT", "/api/v5/repos/:owner/:repo/pull_request_settings", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
```