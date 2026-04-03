#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitCode PR 评论回复脚本
在修复问题后回复评论说明已修复

API 端点:
- 发布评论: POST /repos/:owner/:repo/pulls/:number/comments
- 回复评论: POST /repos/:owner/:repo/pulls/:number/discussions/:discussion_id/comments
"""

import requests
import json
import os
import sys
import argparse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# 设置 stdout 编码为 UTF-8（解决 Windows 终端编码问题）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# GitCode API 基础 URL
BASE_URL = "https://api.gitcode.com/api/v5"


def post_pr_comment(owner: str, repo: str, pr_number: int,
                    body: str, access_token: str,
                    in_reply_to_id: Optional[int] = None,
                    path: Optional[str] = None,
                    position: Optional[int] = None) -> Dict:
    """
    发布 PR 评论

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        pr_number: PR 编号
        body: 评论内容
        access_token: GitCode Token
        in_reply_to_id: 回复的评论 ID
        path: 文件路径（行级评论）
        position: 行号（行级评论）

    Returns:
        API 响应数据
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/comments"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "access_token": access_token,
        "body": body
    }

    # 如果是回复评论
    if in_reply_to_id:
        data["in_reply_to_id"] = in_reply_to_id

    # 如果是行级评论
    if path and position:
        data["path"] = path
        data["position"] = position

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


def reply_to_discussion(owner: str, repo: str, pr_number: int,
                        discussion_id: str, body: str, access_token: str) -> Dict:
    """
    回复 PR 评论（使用 discussion_id，回复会显示在原评论下方）

    API 端点: POST /repos/:owner/:repo/pulls/:number/discussions/:discussion_id/comments

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        pr_number: PR 编号
        discussion_id: 讨论 ID（从评论中获取，用于线程式回复）
        body: 回复内容
        access_token: GitCode Token

    Returns:
        API 响应数据
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/discussions/{discussion_id}/comments"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "access_token": access_token,
        "body": body
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


def generate_fix_reply(commit_sha: str, fix_description: str,
                       issue_title: str = "") -> str:
    """
    生成修复回复内容

    Args:
        commit_sha: 修复提交的 SHA
        fix_description: 修复说明
        issue_title: 问题标题（可选）

    Returns:
        格式化的回复内容
    """
    reply = f"""✅ 此问题已在 commit [{commit_sha[:7]}](链接) 中修复。

**修复内容**: {fix_description}

感谢您的审查！"""

    return reply


def post_detailed_replies(owner: str, repo: str, pr_number: int,
                          access_token: str,
                          detailed_replies: Dict[str, str]) -> Tuple[int, int]:
    """
    回复多个评论，每个回复包含具体修复说明
    使用 discussion_id 进行线程式回复（回复显示在原评论下方）

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        pr_number: PR 编号
        access_token: GitCode Token
        detailed_replies: {discussion_id: fix_description} 映射
                          注意：现在使用 discussion_id 而不是 comment_id

    Returns:
        (成功数, 失败数)
    """
    success_count = 0
    fail_count = 0

    for discussion_id, fix_description in detailed_replies.items():
        try:
            # 生成包含具体修复说明的回复
            reply_body = f"""✅ 已修复：{fix_description}

感谢您的审查！"""

            # 使用 discussion_id 进行线程式回复
            result = reply_to_discussion(
                owner, repo, pr_number,
                discussion_id, reply_body, access_token
            )

            print(f"回复成功: 讨论 {discussion_id[:16]}... - {fix_description}")
            success_count += 1

        except requests.exceptions.HTTPError as e:
            print(f"回复失败: 讨论 {discussion_id[:16]}... - {e}")
            fail_count += 1

    return success_count, fail_count


def reply_to_fixed_issues(owner: str, repo: str, pr_number: int,
                          access_token: str,
                          fixed_issue_ids: List[int],
                          get_comments_func=None) -> Tuple[int, int]:
    """
    回复所有已修复的问题评论（统一回复格式）

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        pr_number: PR 编号
        access_token: GitCode Token
        fixed_issue_ids: 已修复的评论 ID 列表
        get_comments_func: 获取评论的函数（可选，用于获取评论详情）

    Returns:
        (成功数, 失败数)
    """
    success_count = 0
    fail_count = 0

    for comment_id in fixed_issue_ids:
        try:
            # 发布回复（使用 in_reply_to_id）
            # GitCode API 支持回复评论，使用 in_reply_to_id 参数
            reply_body = f"✅ 此问题已修复，感谢您的审查！"

            result = post_pr_comment(
                owner, repo, pr_number,
                reply_body, access_token,
                in_reply_to_id=comment_id
            )

            print(f"回复成功: 评论 #{comment_id}")
            success_count += 1

        except requests.exceptions.HTTPError as e:
            print(f"回复失败: 评论 #{comment_id} - {e}")
            fail_count += 1

    return success_count, fail_count


def post_summary_comment(owner: str, repo: str, pr_number: int,
                         access_token: str,
                         commit_sha: str,
                         fixed_issues: List[Dict]) -> bool:
    """
    发布修复总结评论（整体评论）

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        pr_number: PR 编号
        access_token: GitCode Token
        commit_sha: 提交 SHA
        fixed_issues: 已修复问题列表

    Returns:
        是否发布成功
    """
    # 生成总结内容
    summary = f"""## ✅ 根据 PR 评论修复完成

**提交**: {commit_sha[:7]}

### 修复内容

"""

    for i, issue in enumerate(fixed_issues, 1):
        summary += f"{i}. **{issue.get('title', '问题')}**\n"
        if issue.get('path'):
            summary += f"   - 文件: `{issue['path']}`\n"
        summary += f"   - 修复: {issue.get('fix_description', '已修复')}\n\n"

    summary += "\n感谢所有审查者的宝贵意见！"

    # 发布整体评论（不指定 path 和 position）
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/comments"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "access_token": access_token,
        "body": summary
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("总结评论发布成功！")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"总结评论发布失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="GitCode PR 评论回复工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 发布修复总结（推荐）
  python post_comment_reply.py <token> <owner> <repo> <pr_number> --summary --commit-sha abc123 --fixed-issues "issue1,issue2"

  # 详细回复每个评论（使用 discussion_id，回复显示在原评论下方）
  python post_comment_reply.py <token> <owner> <repo> <pr_number> --detailed-replies '{"b66f1e2e...": "密钥改为环境变量", "...": "添加路径验证"}'

  # 统一回复多个评论（简单回复）
  python post_comment_reply.py <token> <owner> <repo> <pr_number> --fixed-issue-ids "165980011,165980012"

  # 回复指定评论（使用 discussion_id）
  python post_comment_reply.py <token> <owner> <repo> <pr_number> --discussion-id "b66f1e2e..." --message "已修复"

  # 发布单条评论
  python post_comment_reply.py <token> <owner> <repo> <pr_number> --message "感谢审查！"

注意:
  - discussion_id 是长字符串（如 b66f1e2e2d2785b8c57f9cb65525bae04c5c82f2）
  - 从 get_pr_comments.py 的输出中获取 discussion_id
  - 使用 discussion_id 回复会使回复显示在原评论下方（线程式）

环境变量（可选）:
  GITCODE_TOKEN 或 GITCODE_ACCESS_TOKEN: GitCode Token
  REPO_OWNER: 仓库所有者
  REPO_NAME: 仓库名称
  PR_NUMBER: PR 编号
"""
    )

    # 位置参数
    parser.add_argument("token", nargs="?", help="GitCode access_token")
    parser.add_argument("owner", nargs="?", help="仓库所有者")
    parser.add_argument("repo", nargs="?", help="仓库名称")
    parser.add_argument("pr_number", nargs="?", type=int, help="PR 编号")

    # 功能选项
    parser.add_argument("--comment-id", type=int,
                        help="要回复的评论 ID（已弃用，建议使用 --discussion-id）")
    parser.add_argument("--discussion-id",
                        help="讨论 ID（用于线程式回复，回复显示在原评论下方）")
    parser.add_argument("--message", "-m",
                        help="评论/回复内容")
    parser.add_argument("--summary", action="store_true",
                        help="发布修复总结评论")
    parser.add_argument("--commit-sha",
                        help="修复提交 SHA")
    parser.add_argument("--fixed-issues",
                        help="已修复问题列表（逗号分隔）")
    parser.add_argument("--fixed-issue-ids",
                        help="已修复评论 ID 列表（逗号分隔，用于统一回复）")
    parser.add_argument("--detailed-replies",
                        help="详细回复映射（JSON格式：{\"discussion_id\": \"修复说明\"}）")

    parser.add_argument("--path",
                        help="文件路径（行级评论）")
    parser.add_argument("--position", type=int,
                        help="行号（行级评论）")

    args = parser.parse_args()

    # 获取认证信息（优先使用参数，其次使用环境变量）
    access_token = args.token or os.environ.get("GITCODE_TOKEN") or os.environ.get("GITCODE_ACCESS_TOKEN")
    owner = args.owner or os.environ.get("REPO_OWNER")
    repo = args.repo or os.environ.get("REPO_NAME")
    pr_number = args.pr_number or os.environ.get("PR_NUMBER")

    if not access_token:
        print("错误: 需要提供 GitCode Token")
        print("用法: python post_comment_reply.py <token> <owner> <repo> <pr_number> [选项]")
        sys.exit(1)

    if not all([owner, repo, pr_number]):
        print("错误: 需要提供 owner, repo 和 pr_number")
        print("用法: python post_comment_reply.py <token> <owner> <repo> <pr_number> [选项]")
        sys.exit(1)

    pr_number = int(pr_number)

    try:
        if args.summary:
            # 发布修复总结
            if not args.commit_sha:
                print("错误: 发布总结需要 --commit-sha 参数")
                sys.exit(1)

            fixed_issues = []
            if args.fixed_issues:
                # 解析问题列表
                issue_names = args.fixed_issues.split(",")
                fixed_issues = [{"title": name.strip()} for name in issue_names]

            success = post_summary_comment(
                owner, repo, pr_number, access_token,
                args.commit_sha, fixed_issues
            )
            sys.exit(0 if success else 1)

        elif args.detailed_replies:
            # 详细回复多个评论（每个回复包含具体修复说明）
            # 使用 discussion_id 进行线程式回复
            try:
                detailed_map = json.loads(args.detailed_replies)
                success_count, fail_count = post_detailed_replies(
                    owner, repo, pr_number, access_token, detailed_map
                )
                print(f"\n详细回复完成: 成功 {success_count} 条, 失败 {fail_count} 条")
                sys.exit(0 if fail_count == 0 else 1)
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {e}")
                print("格式示例: --detailed-replies '{\"b66f1e2e...\": \"密钥改为环境变量\"}'")
                print("注意: 现在使用 discussion_id（长字符串）而不是 comment_id（数字）")
                sys.exit(1)

        elif args.discussion_id and args.message:
            # 使用 discussion_id 回复单个评论（线程式回复）
            result = reply_to_discussion(
                owner, repo, pr_number,
                args.discussion_id, args.message, access_token
            )
            print(f"回复成功: 讨论 {args.discussion_id[:16]}...")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.fixed_issue_ids:
            # 回复多个已修复的评论
            ids = [int(id.strip()) for id in args.fixed_issue_ids.split(",")]
            success_count, fail_count = reply_to_fixed_issues(
                owner, repo, pr_number, access_token, ids
            )
            print(f"\n回复完成: 成功 {success_count} 条, 失败 {fail_count} 条")
            sys.exit(0 if fail_count == 0 else 1)

        elif args.comment_id and args.message:
            # 回复单个评论
            result = post_pr_comment(
                owner, repo, pr_number, args.message, access_token,
                in_reply_to_id=args.comment_id
            )
            print(f"回复成功: 评论 #{args.comment_id}")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.message:
            # 发布单条评论
            result = post_pr_comment(
                owner, repo, pr_number, args.message, access_token,
                path=args.path,
                position=args.position
            )
            print("评论发布成功！")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        else:
            parser.print_help()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()