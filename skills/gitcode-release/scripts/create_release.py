#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitCode Release 创建工具

支持功能：
- 获取仓库 Tags 列表
- 获取所有/最新/指定 Release 信息
- 创建发行版（Release）
"""

import requests
import json
import os
import sys
import argparse
from typing import List, Optional
from dataclasses import dataclass, field


# Windows 终端 UTF-8 编码处理
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


BASE_URL = "https://api.gitcode.com/api/v5"


@dataclass
class TagInfo:
    """Tag 信息"""
    name: str
    commit_sha: str


@dataclass
class ReleaseInfo:
    """Release 信息"""
    id: int
    tag_name: str
    name: str
    body: str
    created_at: str
    published_at: str = ""
    author: str = ""
    html_url: str = ""
    target_commitish: str = ""


def make_request(endpoint, method='GET', params=None, data=None):
    """统一的 API 请求方法"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method == 'POST':
            response = requests.post(url, headers=headers, params=params, json=data, timeout=30)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, params=params, json=data, timeout=30)
        else:
            raise ValueError(f"不支持的 HTTP 方法: {method}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP 错误: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            status = e.response.status_code
            if status == 401:
                print("认证失败，请检查 access_token 是否正确", file=sys.stderr)
            elif status == 404:
                print("资源不存在或无权访问", file=sys.stderr)
            elif status == 409:
                print("冲突：Tag 或 Release 已存在", file=sys.stderr)
            elif status == 422:
                print("验证失败：请检查参数是否正确", file=sys.stderr)
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}", file=sys.stderr)
                except Exception:
                    print(f"响应内容: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("请求超时，请检查网络连接", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}", file=sys.stderr)
        sys.exit(1)


def get_tags(owner: str, repo: str, access_token: str, per_page: int = 100) -> List[TagInfo]:
    """获取仓库 Tags 列表（自动翻页获取全部）"""
    all_tags = []
    page = 1
    while True:
        endpoint = f"/repos/{owner}/{repo}/tags"
        params = {"access_token": access_token, "page": page, "per_page": per_page}
        result = make_request(endpoint, params=params)
        if not result:
            break
        for item in result:
            commit_sha = ""
            if isinstance(item, dict):
                if "commit" in item and isinstance(item["commit"], dict):
                    commit_sha = item["commit"].get("sha", "")
                elif "id" in item:
                    commit_sha = item.get("id", "")
            all_tags.append(TagInfo(name=item.get("name", ""), commit_sha=commit_sha))
        if len(result) < per_page:
            break
        page += 1
    return all_tags


def get_releases(owner: str, repo: str, access_token: str, per_page: int = 100) -> List[ReleaseInfo]:
    """获取所有 Releases（自动翻页获取全部）"""
    all_releases = []
    page = 1
    while True:
        endpoint = f"/repos/{owner}/{repo}/releases"
        params = {"access_token": access_token, "page": page, "per_page": per_page}
        result = make_request(endpoint, params=params)
        if not result:
            break
        for item in result:
            all_releases.append(_parse_release(item))
        if len(result) < per_page:
            break
        page += 1
    return all_releases


def get_latest_release(owner: str, repo: str, access_token: str) -> Optional[ReleaseInfo]:
    """获取最新 Release"""
    endpoint = f"/repos/{owner}/{repo}/releases/latest"
    params = {"access_token": access_token}
    result = make_request(endpoint, params=params)
    return _parse_release(result)


def get_release_by_tag(owner: str, repo: str, tag: str, access_token: str) -> Optional[ReleaseInfo]:
    """根据 Tag 名称获取 Release"""
    endpoint = f"/repos/{owner}/{repo}/releases/tags/{tag}"
    params = {"access_token": access_token}
    result = make_request(endpoint, params=params)
    return _parse_release(result)


def create_release(owner: str, repo: str, access_token: str,
                   tag_name: str, name: str, body: str,
                   target_commitish: str = "") -> ReleaseInfo:
    """创建发行版"""
    endpoint = f"/repos/{owner}/{repo}/releases"
    params = {"access_token": access_token}
    data = {
        "tag_name": tag_name,
        "name": name,
        "body": body,
    }
    if target_commitish:
        data["target_commitish"] = target_commitish

    result = make_request(endpoint, method='POST', params=params, data=data)
    return _parse_release(result)


def _parse_release(item: dict) -> ReleaseInfo:
    """解析 Release JSON 为 ReleaseInfo"""
    author = ""
    if "author" in item and isinstance(item["author"], dict):
        author = item["author"].get("login", "")

    return ReleaseInfo(
        id=item.get("id", 0),
        tag_name=item.get("tag_name", ""),
        name=item.get("name", ""),
        body=item.get("body", ""),
        created_at=item.get("created_at", ""),
        published_at=item.get("published_at", ""),
        author=author,
        html_url=item.get("html_url", ""),
        target_commitish=item.get("target_commitish", ""),
    )


# ---- 输出格式化 ----

def print_tags(tags: List[TagInfo], json_output: bool = False):
    """输出 Tags 信息"""
    if json_output:
        data = [{"name": t.name, "commit_sha": t.commit_sha} for t in tags]
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if not tags:
        print("暂无 Tag")
        return

    print(f"共 {len(tags)} 个 Tag:\n")
    for tag in tags:
        sha_short = tag.commit_sha[:8] if tag.commit_sha else "N/A"
        print(f"  {tag.name}  (commit: {sha_short})")


def print_release(release: ReleaseInfo, json_output: bool = False):
    """输出单个 Release 信息"""
    if json_output:
        print(json.dumps({
            "id": release.id,
            "tag_name": release.tag_name,
            "name": release.name,
            "body": release.body,
            "created_at": release.created_at,
            "published_at": release.published_at,
            "author": release.author,
            "html_url": release.html_url,
            "target_commitish": release.target_commitish,
        }, ensure_ascii=False, indent=2))
        return

    print(f"Release ID: {release.id}")
    print(f"Tag: {release.tag_name}")
    print(f"标题: {release.name}")
    print(f"作者: {release.author or 'N/A'}")
    print(f"创建时间: {release.created_at}")
    print(f"发布时间: {release.published_at or 'N/A'}")
    print(f"目标分支: {release.target_commitish or 'N/A'}")
    print(f"链接: {release.html_url or 'N/A'}")
    if release.body:
        print(f"\n描述:\n{release.body}")


def print_releases(releases: List[ReleaseInfo], json_output: bool = False):
    """输出多个 Release 信息"""
    if json_output:
        data = [{
            "id": r.id,
            "tag_name": r.tag_name,
            "name": r.name,
            "created_at": r.created_at,
            "html_url": r.html_url,
        } for r in releases]
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if not releases:
        print("暂无 Release")
        return

    print(f"共 {len(releases)} 个 Release:\n")
    for r in releases:
        print(f"  [{r.tag_name}] {r.name}  ({r.created_at})")
        if r.html_url:
            print(f"    {r.html_url}")
        print()


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='GitCode Release 创建工具')

    # 位置参数（可选，可用环境变量替代）
    parser.add_argument('token', nargs='?', default=None,
                        help='GitCode access_token（可用 GITCODE_TOKEN 环境变量）')
    parser.add_argument('owner', nargs='?', default=None,
                        help='仓库所有者（可用 REPO_OWNER 环境变量）')
    parser.add_argument('repo', nargs='?', default=None,
                        help='仓库名称（可用 REPO_NAME 环境变量）')

    # 功能选项（互斥）
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--get-tags', action='store_true',
                              help='获取仓库 Tags 列表')
    action_group.add_argument('--get-latest-release', action='store_true',
                              help='获取最新 Release')
    action_group.add_argument('--get-release', action='store_true',
                              help='获取指定 Tag 的 Release（需配合 --tag）')
    action_group.add_argument('--get-releases', action='store_true',
                              help='获取所有 Releases')
    action_group.add_argument('--create-release', action='store_true',
                              help='创建发行版（需配合 --tag-name, --name, --body/--body-file）')

    # 创建参数
    parser.add_argument('--tag-name', help='Tag 名称（创建发行版时必填）')
    parser.add_argument('--name', help='发行版标题（创建发行版时必填）')
    parser.add_argument('--body', help='发行版描述（直接传文本）')
    parser.add_argument('--body-file', help='发行版描述（从文件读取）')
    parser.add_argument('--target-commitish', default='',
                        help='目标分支或 commit SHA（可选）')

    # 查询参数
    parser.add_argument('--tag', help='查询指定 Tag 的 Release')

    # 输出选项
    parser.add_argument('--json', action='store_true', dest='json_output',
                        help='输出 JSON 格式')

    return parser.parse_args()


def main():
    args = parse_args()

    # 解析参数，优先使用命令行参数，其次使用环境变量
    access_token = args.token or os.environ.get('GITCODE_TOKEN', '')
    owner = args.owner or os.environ.get('REPO_OWNER', '')
    repo = args.repo or os.environ.get('REPO_NAME', '')

    if not access_token:
        print("错误: 缺少 access_token，请通过参数或 GITCODE_TOKEN 环境变量提供", file=sys.stderr)
        sys.exit(1)
    if not owner:
        print("错误: 缺少 owner，请通过参数或 REPO_OWNER 环境变量提供", file=sys.stderr)
        sys.exit(1)
    if not repo:
        print("错误: 缺少 repo，请通过参数或 REPO_NAME 环境变量提供", file=sys.stderr)
        sys.exit(1)

    # 执行对应功能
    if args.get_tags:
        tags = get_tags(owner, repo, access_token)
        print_tags(tags, json_output=args.json_output)

    elif args.get_latest_release:
        release = get_latest_release(owner, repo, access_token)
        if release:
            print_release(release, json_output=args.json_output)
        else:
            print("暂无 Release")

    elif args.get_release:
        if not args.tag:
            print("错误: 获取指定 Release 需要提供 --tag 参数", file=sys.stderr)
            sys.exit(1)
        release = get_release_by_tag(owner, repo, args.tag, access_token)
        print_release(release, json_output=args.json_output)

    elif args.get_releases:
        releases = get_releases(owner, repo, access_token)
        print_releases(releases, json_output=args.json_output)

    elif args.create_release:
        # 验证必填参数
        if not args.tag_name:
            print("错误: 创建发行版需要提供 --tag-name 参数", file=sys.stderr)
            sys.exit(1)
        if not args.name:
            print("错误: 创建发行版需要提供 --name 参数", file=sys.stderr)
            sys.exit(1)

        # 获取 body 内容
        body = ""
        if args.body_file:
            try:
                with open(args.body_file, 'r', encoding='utf-8') as f:
                    body = f.read()
            except FileNotFoundError:
                print(f"错误: 文件不存在: {args.body_file}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"错误: 读取文件失败: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.body:
            body = args.body
        else:
            print("错误: 创建发行版需要提供 --body 或 --body-file 参数", file=sys.stderr)
            sys.exit(1)

        release = create_release(
            owner=owner,
            repo=repo,
            access_token=access_token,
            tag_name=args.tag_name,
            name=args.name,
            body=body,
            target_commitish=args.target_commitish,
        )
        print("发行版创建成功！\n")
        print_release(release, json_output=args.json_output)


if __name__ == '__main__':
    main()
