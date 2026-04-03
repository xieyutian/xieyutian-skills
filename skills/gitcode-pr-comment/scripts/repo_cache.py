#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitCode PR Comment 技能缓存管理脚本
管理仓库 URL 与本地目录的对应关系缓存

缓存文件位置: skills/gitcode-pr-comment/memory/repo_cache.json

支持功能:
- 读取缓存
- 写入缓存
- 验证路径有效性
- 清理无效缓存
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path

# 设置 stdout 编码为 UTF-8（解决 Windows 终端编码问题）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def get_cache_file_path() -> str:
    """
    获取缓存文件的绝对路径
    缓存文件位于技能目录下的 memory 目录
    """
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.parent
    memory_dir = script_dir / "memory"

    # 确保 memory 目录存在
    memory_dir.mkdir(parents=True, exist_ok=True)

    cache_file = memory_dir / "repo_cache.json"
    return str(cache_file)


def load_cache() -> Dict:
    """
    加载缓存文件

    Returns:
        缓存数据字典
    """
    cache_file = get_cache_file_path()

    if not os.path.exists(cache_file):
        # 创建空缓存文件
        empty_cache = {"repos": {}, "version": "1.0", "last_updated": datetime.now().isoformat()}
        save_cache(empty_cache)
        return empty_cache

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"缓存文件读取错误: {e}")
        # 返回空缓存
        return {"repos": {}, "version": "1.0", "last_updated": datetime.now().isoformat()}


def save_cache(cache: Dict) -> bool:
    """
    保存缓存文件

    Args:
        cache: 缓存数据字典

    Returns:
        是否保存成功
    """
    cache_file = get_cache_file_path()

    cache["last_updated"] = datetime.now().isoformat()

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"缓存文件保存错误: {e}")
        return False


def read_repo_cache(repo_url: str) -> Optional[Dict]:
    """
    读取指定仓库的缓存信息

    Args:
        repo_url: 仓库 URL

    Returns:
        缓存信息字典，不存在返回 None
    """
    cache = load_cache()

    repo_info = cache.get("repos", {}).get(repo_url)

    if repo_info:
        # 验证路径有效性
        if validate_path(repo_info.get("local_path", "")):
            return repo_info
        else:
            # 路径无效，清理缓存
            print(f"缓存路径无效: {repo_info.get('local_path')}")
            delete_repo_cache(repo_url)
            return None

    return None


def write_repo_cache(repo_url: str, local_path: str, owner: str = "", repo: str = "") -> bool:
    """
    写入仓库缓存

    Args:
        repo_url: 仓库 URL
        local_path: 本地路径
        owner: 仓库所有者
        repo: 仓库名称

    Returns:
        是否写入成功
    """
    cache = load_cache()

    # 验证路径有效性
    if not validate_path(local_path):
        print(f"路径无效，不写入缓存: {local_path}")
        return False

    # 获取绝对路径
    abs_path = os.path.abspath(local_path)

    cache["repos"][repo_url] = {
        "local_path": abs_path,
        "last_used": datetime.now().isoformat(),
        "owner": owner,
        "repo": repo
    }

    return save_cache(cache)


def delete_repo_cache(repo_url: str) -> bool:
    """
    删除指定仓库的缓存

    Args:
        repo_url: 仓库 URL

    Returns:
        是否删除成功
    """
    cache = load_cache()

    if repo_url in cache.get("repos", {}):
        del cache["repos"][repo_url]
        print(f"已删除缓存: {repo_url}")
        return save_cache(cache)

    print(f"缓存不存在: {repo_url}")
    return False


def validate_path(local_path: str) -> bool:
    """
    验证路径有效性

    Args:
        local_path: 本地路径

    Returns:
        路径是否有效（存在且是 Git 仓库）
    """
    if not local_path:
        return False

    if not os.path.exists(local_path):
        return False

    if not os.path.isdir(local_path):
        return False

    # 检查是否是 Git 仓库
    git_dir = os.path.join(local_path, ".git")
    if not os.path.exists(git_dir):
        return False

    return True


def clean_invalid_cache() -> Tuple[int, int]:
    """
    清理所有无效缓存

    Returns:
        (清理数量, 总数量)
    """
    cache = load_cache()

    cleaned = 0
    total = len(cache.get("repos", {}))

    invalid_urls = []

    for repo_url, repo_info in cache.get("repos", {}).items():
        if not validate_path(repo_info.get("local_path", "")):
            invalid_urls.append(repo_url)

    for url in invalid_urls:
        del cache["repos"][url]
        cleaned += 1
        print(f"清理无效缓存: {url}")

    if cleaned > 0:
        save_cache(cache)

    return cleaned, total


def clone_repo(repo_url: str, owner: str, repo: str, base_dir: str = None) -> Tuple[bool, str]:
    """
    克隆仓库到本地

    Args:
        repo_url: 仓库 URL
        owner: 仓库所有者
        repo: 仓库名称
        base_dir: 基础目录（默认为用户主目录下的 gitcode_repos）

    Returns:
        (是否成功, 本地路径或错误信息)
    """
    import subprocess

    # 确定基础目录
    if not base_dir:
        base_dir = os.path.join(str(Path.home()), "gitcode_repos")

    # 确保基础目录存在
    os.makedirs(base_dir, exist_ok=True)

    # 生成仓库目录名：owner_repo
    repo_dir_name = f"{owner}_{repo}"
    local_path = os.path.join(base_dir, repo_dir_name)

    # 检查目录是否已存在
    if os.path.exists(local_path):
        # 目录已存在，检查是否是正确的仓库
        if validate_path(local_path):
            return True, local_path
        else:
            # 目录存在但不是有效仓库，删除后重新克隆
            import shutil
            shutil.rmtree(local_path)

    # 执行克隆
    print(f"正在克隆仓库: {repo_url}")
    print(f"目标目录: {local_path}")

    try:
        result = subprocess.run(
            ["git", "clone", repo_url, local_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            print(f"克隆成功: {local_path}")
            return True, local_path
        else:
            error_msg = result.stderr or result.stdout or "未知错误"
            print(f"克隆失败: {error_msg}")
            return False, error_msg

    except subprocess.TimeoutExpired:
        print("克隆超时")
        return False, "克隆超时"
    except Exception as e:
        print(f"克隆异常: {e}")
        return False, str(e)


def get_or_clone_repo(repo_url: str, owner: str, repo: str) -> Tuple[str, bool]:
    """
    获取仓库本地路径，如果不存在则自动克隆

    Args:
        repo_url: 仓库 URL
        owner: 仓库所有者
        repo: 仓库名称

    Returns:
        (本地路径, 是否新克隆)
    """
    # 1. 先检查缓存
    cached = read_repo_cache(repo_url)
    if cached:
        return cached.get("local_path"), False

    # 2. 缓存不存在，自动克隆
    success, result = clone_repo(repo_url, owner, repo)
    if success:
        # 写入缓存
        write_repo_cache(repo_url, result, owner, repo)
        return result, True
    else:
        raise RuntimeError(f"无法获取仓库: {result}")


def list_all_cache() -> Dict:
    """
    列出所有缓存

    Returns:
        缓存数据字典
    """
    cache = load_cache()

    print("=" * 60)
    print("仓库缓存列表")
    print("=" * 60)

    if not cache.get("repos"):
        print("\n无缓存记录")
        return cache

    print(f"\n总计: {len(cache['repos'])} 条缓存\n")

    for i, (repo_url, repo_info) in enumerate(cache["repos"].items(), 1):
        print(f"  [{i}] {repo_url}")
        print(f"      本地路径: {repo_info.get('local_path')}")
        print(f"      最后使用: {repo_info.get('last_used')}")
        print(f"      有效性: {validate_path(repo_info.get('local_path', ''))}")
        print()

    return cache


def main():
    parser = argparse.ArgumentParser(
        description="GitCode PR Comment 缓存管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 获取或克隆仓库（推荐：自动处理缓存和克隆）
  python repo_cache.py --get "https://gitcode.com/owner/repo.git" --owner owner --repo repo

  # 只克隆仓库（不检查缓存）
  python repo_cache.py --clone "https://gitcode.com/owner/repo.git" --owner owner --repo repo

  # 读取缓存
  python repo_cache.py --read "https://gitcode.com/owner/repo.git"

  # 写入缓存（手动指定本地路径）
  python repo_cache.py --write "https://gitcode.com/owner/repo.git" "/path/to/local/repo" --owner owner --repo repo

  # 验证路径
  python repo_cache.py --validate "/path/to/local/repo"

  # 删除缓存
  python repo_cache.py --delete "https://gitcode.com/owner/repo.git"

  # 清理无效缓存
  python repo_cache.py --clean

  # 列出所有缓存
  python repo_cache.py --list
"""
    )

    parser.add_argument("--get", metavar="URL", help="获取仓库本地路径（缓存不存在则自动克隆）")
    parser.add_argument("--clone", metavar="URL", help="克隆仓库到本地")
    parser.add_argument("--read", metavar="URL", help="读取指定仓库的缓存")
    parser.add_argument("--write", nargs=2, metavar=("URL", "PATH"),
                        help="写入仓库缓存 (URL PATH)")
    parser.add_argument("--owner", default="", help="仓库所有者（配合 --get/--clone/--write 使用）")
    parser.add_argument("--repo", default="", help="仓库名称（配合 --get/--clone/--write 使用）")
    parser.add_argument("--validate", metavar="PATH", help="验证路径有效性")
    parser.add_argument("--delete", metavar="URL", help="删除指定仓库的缓存")
    parser.add_argument("--clean", action="store_true", help="清理所有无效缓存")
    parser.add_argument("--list", action="store_true", help="列出所有缓存")

    args = parser.parse_args()

    # 执行对应操作
    if args.get:
        # 获取或克隆仓库
        if not args.owner or not args.repo:
            print("错误: --get 需要 --owner 和 --repo 参数")
            sys.exit(1)
        try:
            local_path, is_new = get_or_clone_repo(args.get, args.owner, args.repo)
            result = {
                "local_path": local_path,
                "is_new_clone": is_new,
                "repo_url": args.get
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except RuntimeError as e:
            print(f"错误: {e}")
            sys.exit(1)

    elif args.clone:
        # 只克隆仓库
        if not args.owner or not args.repo:
            print("错误: --clone 需要 --owner 和 --repo 参数")
            sys.exit(1)
        success, result = clone_repo(args.clone, args.owner, args.repo)
        if success:
            # 写入缓存
            write_repo_cache(args.clone, result, args.owner, args.repo)
            output = {
                "success": True,
                "local_path": result,
                "repo_url": args.clone
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"克隆失败: {result}")
            sys.exit(1)

    elif args.read:
        repo_info = read_repo_cache(args.read)
        if repo_info:
            print(json.dumps(repo_info, indent=2, ensure_ascii=False))
        else:
            print("缓存不存在或路径无效")
            sys.exit(1)

    elif args.write:
        repo_url, local_path = args.write
        success = write_repo_cache(repo_url, local_path, args.owner, args.repo)
        if success:
            print(f"缓存写入成功: {repo_url} -> {local_path}")
        else:
            print("缓存写入失败")
            sys.exit(1)

    elif args.validate:
        valid = validate_path(args.validate)
        print(f"路径有效性: {valid}")
        sys.exit(0 if valid else 1)

    elif args.delete:
        success = delete_repo_cache(args.delete)
        sys.exit(0 if success else 1)

    elif args.clean:
        cleaned, total = clean_invalid_cache()
        print(f"\n清理完成: {cleaned}/{total} 条无效缓存已删除")

    elif args.list:
        list_all_cache()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()