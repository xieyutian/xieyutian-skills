#!/usr/bin/env python3
"""
GitCode PR 信息获取脚本
获取指定 Pull Request 的详细信息和审查上下文

支持功能：
- 获取 PR 基本信息（标题、描述、状态等）
- 获取 PR 文件变更列表
- 获取 PR commits 信息
- 输出审查上下文（用于代码审查）
"""

import requests
import json
import os
import sys
import argparse
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


# GitCode API 基础 URL
BASE_URL = "https://api.gitcode.com/api/v5"


@dataclass
class PRFile:
    """PR 文件变更信息"""
    filename: str
    status: str  # added, modified, removed, renamed
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None


@dataclass
class PRCommit:
    """PR commit 信息"""
    sha: str
    message: str
    author: str
    date: str


@dataclass
class PRInfo:
    """PR 基本信息"""
    number: int
    title: str
    state: str
    body: str
    user: str
    created_at: str
    updated_at: str
    head_branch: str
    head_sha: str
    base_branch: str
    base_sha: str
    merged: bool
    merged_at: Optional[str] = None
    merged_by: Optional[str] = None
    html_url: str = ""
    labels: List[str] = field(default_factory=list)
    assignees: List[str] = field(default_factory=list)


def get_pull_request(owner: str, repo: str, pr_number: int, access_token: str) -> PRInfo:
    """
    获取 GitCode Pull Request 基本信息

    Args:
        owner: 仓库所属空间地址（组织或个人）
        repo: 仓库名称
        pr_number: PR 编号
        access_token: 用户授权码

    Returns:
        PRInfo 对象
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
    params = {"access_token": access_token}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return PRInfo(
        number=data.get("number", 0),
        title=data.get("title", ""),
        state=data.get("state", ""),
        body=data.get("body", "") or "",
        user=data.get("user", {}).get("login", "N/A"),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
        head_branch=data.get("head", {}).get("ref", ""),
        head_sha=data.get("head", {}).get("sha", ""),
        base_branch=data.get("base", {}).get("ref", ""),
        base_sha=data.get("base", {}).get("sha", ""),
        merged=data.get("merged", False),
        merged_at=data.get("merged_at"),
        merged_by=data.get("merged_by", {}).get("login") if data.get("merged_by") else None,
        html_url=data.get("html_url", ""),
        labels=[label.get("name", "") for label in data.get("labels", [])],
        assignees=[a.get("login", "") for a in data.get("assignees", [])]
    )


def get_pr_files(owner: str, repo: str, pr_number: int, access_token: str) -> List[PRFile]:
    """
    获取 PR 文件变更列表

    Args:
        owner: 仓库所属空间地址
        repo: 仓库名称
        pr_number: PR 编号
        access_token: 用户授权码

    Returns:
        PRFile 列表
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/files"
    params = {"access_token": access_token}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    files = []
    for item in data:
        files.append(PRFile(
            filename=item.get("filename", ""),
            status=item.get("status", ""),
            additions=item.get("additions", 0),
            deletions=item.get("deletions", 0),
            changes=item.get("changes", 0),
            patch=item.get("patch")
        ))

    return files


def get_pr_commits(owner: str, repo: str, pr_number: int, access_token: str) -> List[PRCommit]:
    """
    获取 PR commits 信息

    Args:
        owner: 仓库所属空间地址
        repo: 仓库名称
        pr_number: PR 编号
        access_token: 用户授权码

    Returns:
        PRCommit 列表
    """
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    params = {"access_token": access_token}

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    commits = []
    for item in data:
        commit_data = item.get("commit", {})
        commits.append(PRCommit(
            sha=item.get("sha", "")[:7],
            message=commit_data.get("message", "").split("\n")[0],  # 只取第一行
            author=commit_data.get("author", {}).get("name", "N/A"),
            date=commit_data.get("author", {}).get("date", "")
        ))

    return commits


def extract_modification_points(body: str) -> List[str]:
    """
    从 PR 描述中提取声称的修改点

    Args:
        body: PR 描述内容

    Returns:
        修改点列表
    """
    if not body:
        return []

    points = []

    # 尝试匹配常见的修改描述格式
    patterns = [
        # 匹配 "- xxx" 或 "* xxx" 列表项
        r"[-*]\s*(.+?)(?=\n[-*]|\n\n|\n##|$)",
        # 匹配数字列表 "1. xxx"
        r"\d+\.\s*(.+?)(?=\n\d+\.|\n\n|\n##|$)",
        # 匹配 "修改了 xxx" 或 "修复了 xxx" 等描述
        r"(?:修改|修复|新增|删除|更新|优化|重构)[了]?\s*(.+?)(?:\n|$)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, body, re.MULTILINE | re.DOTALL)
        for match in matches:
            point = match.strip()
            if point and len(point) > 5 and point not in points:
                points.append(point)

    # 如果没有匹配到，尝试按行分割
    if not points:
        lines = body.split("\n")
        for line in lines:
            line = line.strip()
            # 过滤掉太短或明显不是修改描述的行
            if len(line) > 10 and not line.startswith("#") and not line.startswith("```"):
                if any(kw in line for kw in ["修改", "修复", "新增", "删除", "更新", "优化", "fix", "add", "update", "remove", "change"]):
                    points.append(line)

    return points[:10]  # 最多返回 10 个修改点


def print_pr_basic_info(pr_info: PRInfo):
    """打印 PR 基本信息"""
    print("=" * 60)
    print(f"PR #{pr_info.number}: {pr_info.title}")
    print("=" * 60)
    print(f"状态: {pr_info.state}")
    print(f"创建者: {pr_info.user}")
    print(f"创建时间: {pr_info.created_at}")
    print(f"更新时间: {pr_info.updated_at}")
    print(f"源分支: {pr_info.head_branch} ({pr_info.head_sha[:7]})")
    print(f"目标分支: {pr_info.base_branch} ({pr_info.base_sha[:7]})")

    if pr_info.merged:
        print(f"已合并: 是")
        if pr_info.merged_at:
            print(f"合并时间: {pr_info.merged_at}")
        if pr_info.merged_by:
            print(f"合并者: {pr_info.merged_by}")
    else:
        print(f"已合并: 否")

    if pr_info.labels:
        print(f"标签: {', '.join(pr_info.labels)}")

    if pr_info.assignees:
        print(f"审查者: {', '.join(pr_info.assignees)}")

    print(f"\n链接: {pr_info.html_url}")

    if pr_info.body:
        print(f"\n描述:\n{pr_info.body}")


def print_pr_files(files: List[PRFile], show_patch: bool = False):
    """打印 PR 文件变更列表"""
    print("\n" + "=" * 60)
    print(f"文件变更 ({len(files)} 个文件)")
    print("=" * 60)

    # 统计
    added = [f for f in files if f.status == "added"]
    modified = [f for f in files if f.status == "modified"]
    removed = [f for f in files if f.status == "removed"]
    renamed = [f for f in files if f.status == "renamed"]

    total_additions = sum(f.additions for f in files)
    total_deletions = sum(f.deletions for f in files)

    print(f"\n统计:")
    print(f"  新增: {len(added)} | 修改: {len(modified)} | 删除: {len(removed)} | 重命名: {len(renamed)}")
    print(f"  +{total_additions} 行, -{total_deletions} 行")

    print(f"\n文件列表:")
    for f in files:
        status_icon = {
            "added": "[+]",
            "modified": "[~]",
            "removed": "[-]",
            "renamed": "[>]"
        }.get(f.status, "[?]")

        print(f"  {status_icon} {f.filename} (+{f.additions}/-{f.deletions})")

        if show_patch and f.patch:
            print(f"    Patch preview:")
            for line in f.patch.split("\n")[:5]:  # 只显示前 5 行
                print(f"      {line}")
            if len(f.patch.split("\n")) > 5:
                print(f"      ...")


def print_pr_commits(commits: List[PRCommit]):
    """打印 PR commits 信息"""
    print("\n" + "=" * 60)
    print(f"Commits ({len(commits)} 个)")
    print("=" * 60)

    for c in commits:
        print(f"  [{c.sha}] {c.message}")
        print(f"          by {c.author} at {c.date}")


def print_review_context(pr_info: PRInfo, files: List[PRFile], commits: List[PRCommit]):
    """
    打印审查上下文信息
    用于代码审查时了解 PR 的修改内容和声称的修改点
    """
    print("=" * 60)
    print("[PR 审查上下文]")
    print("=" * 60)

    # PR 基本信息
    print(f"\n【基本信息】")
    print(f"PR #{pr_info.number}: {pr_info.title}")
    print(f"作者: {pr_info.user}")
    print(f"状态: {pr_info.state}")
    print(f"源分支: {pr_info.head_branch} -> 目标分支: {pr_info.base_branch}")

    # 提取并显示声称的修改点
    print(f"\n【声称的修改点】")
    modification_points = extract_modification_points(pr_info.body)

    if modification_points:
        for i, point in enumerate(modification_points, 1):
            print(f"  {i}. {point}")
    else:
        print("  (无法从描述中提取明确的修改点，请手动分析)")

    # 文件变更统计
    print(f"\n【文件变更统计】")
    added = [f for f in files if f.status == "added"]
    modified = [f for f in files if f.status == "modified"]
    removed = [f for f in files if f.status == "removed"]

    total_additions = sum(f.additions for f in files)
    total_deletions = sum(f.deletions for f in files)

    print(f"  新增: {len(added)} | 修改: {len(modified)} | 删除: {len(removed)}")
    print(f"  +{total_additions} 行, -{total_deletions} 行")

    # 按文件类型分组
    print(f"\n【变更文件列表】")
    by_ext = {}
    for f in files:
        ext = f.filename.rsplit(".", 1)[-1] if "." in f.filename else "other"
        if ext not in by_ext:
            by_ext[ext] = []
        by_ext[ext].append(f)

    for ext, file_list in sorted(by_ext.items()):
        print(f"\n  .{ext} 文件 ({len(file_list)} 个):")
        for f in file_list:
            status_icon = {
                "added": "🟢",
                "modified": "🟡",
                "removed": "🔴",
                "renamed": "🔵"
            }.get(f.status, "[?]")
            print(f"    {status_icon} {f.filename}")

    # Commits 信息
    print(f"\n【Commits ({len(commits)} 个)】")
    for c in commits[:5]:  # 最多显示 5 个
        print(f"  [{c.sha}] {c.message}")
    if len(commits) > 5:
        print(f"  ... 还有 {len(commits) - 5} 个 commits")

    # 审查提示
    print(f"\n【审查提示】")
    print(f"  1. 请对照声称的修改点，检查是否都已实现")
    print(f"  2. 检查是否有遗漏的文件或代码路径")
    print(f"  3. 验证修改的逻辑正确性")
    print(f"  4. 检查是否需要添加测试用例")

    # 输出用于 AI 审查的结构化数据
    print("\n" + "=" * 60)
    print("[结构化数据] (供 AI 审查使用)")
    print("=" * 60)

    context_data = {
        "pr_number": pr_info.number,
        "title": pr_info.title,
        "author": pr_info.user,
        "state": pr_info.state,
        "description": pr_info.body,
        "modification_points": modification_points,
        "files": [
            {
                "filename": f.filename,
                "status": f.status,
                "additions": f.additions,
                "deletions": f.deletions
            }
            for f in files
        ],
        "commits": [
            {
                "sha": c.sha,
                "message": c.message,
                "author": c.author
            }
            for c in commits
        ]
    }

    print(json.dumps(context_data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="GitCode PR 信息获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 获取 PR 基本信息
  python get_pr_info.py <token> <owner> <repo> <pr_number>

  # 获取完整审查上下文
  python get_pr_info.py <token> <owner> <repo> <pr_number> --review-context

  # 只获取文件变更列表
  python get_pr_info.py <token> <owner> <repo> <pr_number> --files

  # 获取 commits 信息
  python get_pr_info.py <token> <owner> <repo> <pr_number> --commits
"""
    )

    parser.add_argument("token", nargs="?", help="GitCode access_token")
    parser.add_argument("owner", nargs="?", help="仓库所有者")
    parser.add_argument("repo", nargs="?", help="仓库名称")
    parser.add_argument("pr_number", nargs="?", type=int, help="PR 编号")

    parser.add_argument("--review-context", action="store_true",
                        help="输出完整审查上下文（默认）")
    parser.add_argument("--files", action="store_true",
                        help="输出文件变更列表")
    parser.add_argument("--commits", action="store_true",
                        help="输出 commits 信息")
    parser.add_argument("--show-patch", action="store_true",
                        help="显示文件 patch 预览")
    parser.add_argument("--json", action="store_true",
                        help="输出 JSON 格式")

    args = parser.parse_args()

    # 获取认证信息
    access_token = args.token or os.environ.get("GITCODE_ACCESS_TOKEN")
    owner = args.owner or os.environ.get("REPO_OWNER")
    repo = args.repo or os.environ.get("REPO_NAME")
    pr_number = args.pr_number or os.environ.get("PR_NUMBER")

    if not access_token:
        print("错误: 需要提供 GitCode access_token")
        print("\n使用方法:")
        print("  1. 作为参数: python get_pr_info.py <token> <owner> <repo> <pr_number>")
        print("  2. 设置环境变量: export GITCODE_ACCESS_TOKEN=your_token")
        print("\n获取 token: https://gitcode.com/-/profile/personal_access_tokens")
        sys.exit(1)

    if not all([owner, repo, pr_number]):
        print("错误: 需要提供 owner, repo 和 pr_number")
        print("用法: python get_pr_info.py <token> <owner> <repo> <pr_number>")
        sys.exit(1)

    pr_number = int(pr_number)

    try:
        print(f"正在获取 PR 信息: {owner}/{repo}#{pr_number}...")

        # 获取 PR 基本信息
        pr_info = get_pull_request(owner, repo, pr_number, access_token)

        # 根据参数决定输出内容
        if args.files:
            files = get_pr_files(owner, repo, pr_number, access_token)
            print_pr_files(files, show_patch=args.show_patch)
        elif args.commits:
            commits = get_pr_commits(owner, repo, pr_number, access_token)
            print_pr_commits(commits)
        elif args.json:
            files = get_pr_files(owner, repo, pr_number, access_token)
            commits = get_pr_commits(owner, repo, pr_number, access_token)
            context_data = {
                "pr_number": pr_info.number,
                "title": pr_info.title,
                "author": pr_info.user,
                "state": pr_info.state,
                "description": pr_info.body,
                "modification_points": extract_modification_points(pr_info.body),
                "files": [{"filename": f.filename, "status": f.status, "additions": f.additions, "deletions": f.deletions} for f in files],
                "commits": [{"sha": c.sha, "message": c.message, "author": c.author} for c in commits]
            }
            print(json.dumps(context_data, indent=2, ensure_ascii=False))
        else:
            # 默认输出审查上下文
            files = get_pr_files(owner, repo, pr_number, access_token)
            commits = get_pr_commits(owner, repo, pr_number, access_token)
            print_review_context(pr_info, files, commits)

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