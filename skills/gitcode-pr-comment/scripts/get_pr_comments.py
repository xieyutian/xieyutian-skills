#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitCode PR 评论获取脚本
获取指定 Pull Request 的所有评论信息

支持功能：
- 获取 PR 所有评论（包括代码行评论和整体评论）
- 按评论类型筛选
- 输出结构化 JSON 数据

API 端点: GET /repos/:owner/:repo/pulls/:number/comments
"""

import requests
import json
import os
import sys
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

# 设置 stdout 编码为 UTF-8（解决 Windows 终端编码问题）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# GitCode API 基础 URL
BASE_URL = "https://api.gitcode.com/api/v5"


@dataclass
class PRComment:
    """PR 评论信息"""
    id: int
    body: str
    user: str
    created_at: str
    discussion_id: str = ""  # 讨论ID，用于回复评论（重要！）
    updated_at: Optional[str] = None
    # 行级评论特有字段
    path: Optional[str] = None  # 文件路径
    position: Optional[int] = None  # 行号
    original_position: Optional[int] = None
    commit_id: Optional[str] = None
    # 新增：详细的行号位置信息
    diff_position: Optional[Dict] = None  # {"start_new_line": 10, "end_new_line": 12}
    # 评论类型
    comment_type: str = "pr_comment"  # diff_comment 或 pr_comment
    # HTML URL
    html_url: str = ""


def get_pr_comments(owner: str, repo: str, pr_number: int, access_token: str,
                    comment_type: Optional[str] = None,
                    page: int = 1, per_page: int = 100) -> List[PRComment]:
    """
    获取 GitCode Pull Request 的所有评论

    Args:
        owner: 仓库所属空间地址（组织或个人）
        repo: 仓库名称
        pr_number: PR 编号
        access_token: 用户授权码
        comment_type: 评论类型筛选 (diff_comment/pr_comment/None)
        page: 页码
        per_page: 每页数量

    Returns:
        PRComment 列表
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/comments"
    params = {
        "access_token": access_token,
        "page": page,
        "per_page": per_page,
        "direction": "desc"  # 最新评论在前
    }

    if comment_type:
        params["comment_type"] = comment_type

    comments = []

    while True:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        for item in data:
            # 判断评论类型 - 使用 API 返回的类型，更准确
            api_comment_type = item.get("comment_type", "")
            if api_comment_type:
                ctype = api_comment_type  # 优先使用 API 返回的类型
            else:
                # 兼容旧逻辑：有 path 和 position 的评论是代码行评论
                ctype = "diff_comment" if item.get("path") else "pr_comment"

            comments.append(PRComment(
                id=item.get("id", 0),
                body=item.get("body", "") or "",
                user=item.get("user", {}).get("login", "N/A"),
                created_at=item.get("created_at", ""),
                discussion_id=item.get("discussion_id", ""),  # 重要：用于回复评论
                updated_at=item.get("updated_at"),
                path=item.get("path"),
                position=item.get("position"),
                original_position=item.get("original_position"),
                commit_id=item.get("commit_id"),
                diff_position=item.get("diff_position"),  # 详细行号信息
                comment_type=ctype,
                html_url=item.get("html_url", "")
            ))

        # 检查是否还有下一页
        if len(data) < per_page:
            break
        params["page"] += 1

    return comments


def print_comments_summary(comments: List[PRComment]):
    """打印评论摘要"""
    print("=" * 60)
    print("PR 评论摘要")
    print("=" * 60)

    # 分类统计
    diff_comments = [c for c in comments if c.comment_type == "diff_comment"]
    pr_comments = [c for c in comments if c.comment_type == "pr_comment"]

    print(f"\n总计: {len(comments)} 条评论")
    print(f"  - 代码行评论: {len(diff_comments)} 条")
    print(f"  - 整体评论: {len(pr_comments)} 条")

    # 显示代码行评论
    if diff_comments:
        print(f"\n【代码行评论】")
        for c in diff_comments:
            print(f"  ID: {c.id}")
            print(f"    作者: {c.user}")
            print(f"    文件: {c.path}#{c.position}")
            print(f"    内容: {c.body[:100]}{'...' if len(c.body) > 100 else ''}")
            print(f"    时间: {c.created_at}")
            print()

    # 显示整体评论
    if pr_comments:
        print(f"\n【整体评论】")
        for c in pr_comments:
            print(f"  ID: {c.id}")
            print(f"    作者: {c.user}")
            print(f"    内容: {c.body[:100]}{'...' if len(c.body) > 100 else ''}")
            print(f"    时间: {c.created_at}")
            print()


def print_comments_json(comments: List[PRComment]):
    """打印 JSON 格式输出"""
    diff_comments = [c for c in comments if c.comment_type == "diff_comment"]
    pr_comments = [c for c in comments if c.comment_type == "pr_comment"]

    result = {
        "pr_number": 0,  # 需要从外部传入
        "total_comments": len(comments),
        "diff_comments_count": len(diff_comments),
        "pr_comments_count": len(pr_comments),
        "diff_comments": [
            {
                "id": c.id,
                "discussion_id": c.discussion_id,  # 用于回复评论
                "body": c.body,
                "user": c.user,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "path": c.path,
                "position": c.position,
                "diff_position": c.diff_position,  # 详细行号
                "commit_id": c.commit_id,
                "html_url": c.html_url
            }
            for c in diff_comments
        ],
        "pr_comments": [
            {
                "id": c.id,
                "discussion_id": c.discussion_id,  # 用于回复评论
                "body": c.body,
                "user": c.user,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "html_url": c.html_url
            }
            for c in pr_comments
        ]
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


def print_analysis_context(comments: List[PRComment]):
    """
    打印评论分析上下文
    用于后续 AI 分析评论有效性
    """
    print("=" * 60)
    print("[评论分析上下文]")
    print("=" * 60)

    diff_comments = [c for c in comments if c.comment_type == "diff_comment"]
    pr_comments = [c for c in comments if c.comment_type == "pr_comment"]

    print(f"\n【评论统计】")
    print(f"  代码行评论: {len(diff_comments)} 条")
    print(f"  整体评论: {len(pr_comments)} 条")

    # 分析代码行评论
    if diff_comments:
        print(f"\n【代码行评论详情】（用于问题分析）")
        for i, c in enumerate(diff_comments, 1):
            print(f"\n  --- 评论 #{i} ---")
            print(f"  文件: {c.path}")
            print(f"  行号: {c.position}")
            if c.diff_position:
                print(f"  详细位置: {c.diff_position}")
            print(f"  作者: {c.user}")
            print(f"  评论内容:")
            # 格式化显示评论内容
            for line in c.body.split("\n"):
                print(f"    {line}")
            print(f"  评论 ID: {c.id}")
            print(f"  讨论 ID: {c.discussion_id}")  # 重要：用于回复
            print(f"  创建时间: {c.created_at}")

    # 分析整体评论
    if pr_comments:
        print(f"\n【整体评论详情】")
        for i, c in enumerate(pr_comments, 1):
            print(f"\n  --- 评论 #{i} ---")
            print(f"  作者: {c.user}")
            print(f"  评论内容:")
            for line in c.body.split("\n"):
                print(f"    {line}")
            print(f"  评论 ID: {c.id}")
            print(f"  讨论 ID: {c.discussion_id}")  # 重要：用于回复
            print(f"  创建时间: {c.created_at}")

    # 输出结构化数据
    print("\n" + "=" * 60)
    print("[结构化数据] (供 AI 分析使用)")
    print("=" * 60)

    context_data = {
        "total_comments": len(comments),
        "diff_comments": [
            {
                "id": c.id,
                "discussion_id": c.discussion_id,  # 用于回复评论
                "body": c.body,
                "user": c.user,
                "path": c.path,
                "position": c.position,
                "diff_position": c.diff_position,
                "created_at": c.created_at
            }
            for c in diff_comments
        ],
        "pr_comments": [
            {
                "id": c.id,
                "discussion_id": c.discussion_id,  # 用于回复评论
                "body": c.body,
                "user": c.user,
                "created_at": c.created_at
            }
            for c in pr_comments
        ]
    }

    print(json.dumps(context_data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="GitCode PR 评论获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 获取 PR 所有评论
  python get_pr_comments.py <token> <owner> <repo> <pr_number>

  # 只获取代码行评论
  python get_pr_comments.py <token> <owner> <repo> <pr_number> --type diff_comment

  # 只获取整体评论
  python get_pr_comments.py <token> <owner> <repo> <pr_number> --type pr_comment

  # 输出 JSON 格式
  python get_pr_comments.py <token> <owner> <repo> <pr_number> --json

  # 输出分析上下文（用于 AI 分析）
  python get_pr_comments.py <token> <owner> <repo> <pr_number> --analysis
"""
    )

    parser.add_argument("token", nargs="?", help="GitCode access_token")
    parser.add_argument("owner", nargs="?", help="仓库所有者")
    parser.add_argument("repo", nargs="?", help="仓库名称")
    parser.add_argument("pr_number", nargs="?", type=int, help="PR 编号")

    parser.add_argument("--type", choices=["diff_comment", "pr_comment"],
                        help="评论类型筛选: diff_comment(代码行评论) 或 pr_comment(整体评论)")
    parser.add_argument("--json", action="store_true",
                        help="输出 JSON 格式")
    parser.add_argument("--analysis", action="store_true",
                        help="输出评论分析上下文")

    args = parser.parse_args()

    # 获取认证信息
    access_token = args.token or os.environ.get("GITCODE_TOKEN") or os.environ.get("GITCODE_ACCESS_TOKEN")
    owner = args.owner or os.environ.get("REPO_OWNER")
    repo = args.repo or os.environ.get("REPO_NAME")
    pr_number = args.pr_number or os.environ.get("PR_NUMBER")

    if not access_token:
        print("错误: 需要提供 GitCode access_token")
        print("\n使用方法:")
        print("  1. 作为参数: python get_pr_comments.py <token> <owner> <repo> <pr_number>")
        print("  2. 设置环境变量: export GITCODE_TOKEN=your_token")
        print("\n获取 token: https://gitcode.com/-/profile/personal_access_tokens")
        sys.exit(1)

    if not all([owner, repo, pr_number]):
        print("错误: 需要提供 owner, repo 和 pr_number")
        print("用法: python get_pr_comments.py <token> <owner> <repo> <pr_number>")
        sys.exit(1)

    pr_number = int(pr_number)

    try:
        print(f"正在获取 PR 评论: {owner}/{repo}#{pr_number}...")

        # 获取评论
        comments = get_pr_comments(owner, repo, pr_number, access_token,
                                   comment_type=args.type)

        # 根据参数决定输出内容
        if args.json:
            print_comments_json(comments)
        elif args.analysis:
            print_analysis_context(comments)
        else:
            print_comments_summary(comments)

    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误: {e}")
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 401:
                print("认证失败，请检查 access_token 是否正确")
            elif e.response.status_code == 404:
                print("PR 不存在或无权访问")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()