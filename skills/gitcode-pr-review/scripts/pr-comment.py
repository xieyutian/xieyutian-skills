#!/usr/bin/env python3
"""
GitCode PR 评论发布工具

支持两种评论模式：
1. 整体评论：普通 PR 评论
2. 行级评论：针对特定文件和代码行的评论

可以解析代码审查报告，自动将潜在问题发布为行级评论，将改进建议发布为整体评论。
"""

import os
import re
import requests
import sys
import argparse
from typing import List, Dict, Optional, Tuple

# GitCode API 基础 URL
BASE_URL = "https://api.gitcode.com/api/v5"


def post_comment_to_gitcode(repo_owner: str, repo_name: str, pr_number: str, 
                            comment_body: str, token: str,
                            path: Optional[str] = None, 
                            position: Optional[int] = None) -> bool:
    """
    发布评论到 GitCode PR
    
    Args:
        repo_owner: 仓库所有者
        repo_name: 仓库名称
        pr_number: PR 编号
        comment_body: 评论内容
        token: GitCode Token
        path: 文件路径（行级评论时需要）
        position: 代码行号（行级评论时需要）
    
    Returns:
        是否发布成功
    """
    url = f"{BASE_URL}/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "body": comment_body
    }
    
    # 如果提供了 path 和 position，添加到请求数据中（行级评论）
    if path and position:
        data["path"] = path
        data["position"] = position
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        if path and position:
            print(f"行级评论发布成功！文件: {path}, 行号: {position}")
        else:
            print("整体评论发布成功！")
        return True
    else:
        print(f"发布失败: {response.status_code}")
        print(response.text)
        return False


def parse_code_block(code_block: str) -> Tuple[Optional[str], Optional[int], str]:
    """
    解析代码块，提取文件路径、行号和代码内容
    
    代码块格式示例：
    ```cj:src/main.cj#L20-L25
    代码内容
    ```
    
    或简单格式：
    ```cj:src/main.cj#L20
    代码内容
    ```
    
    Args:
        code_block: 代码块字符串
    
    Returns:
        (文件路径, 起始行号, 代码内容)
    """
    # 匹配代码块开头：```语言:文件路径#L行号
    pattern = r"```(\w+)?(?::([^#\n]+))?(?:#L(\d+)(?:-L(\d+))?)?\n([\s\S]*?)```"
    match = re.search(pattern, code_block)
    
    if match:
        language = match.group(1)
        file_path = match.group(2)
        start_line = int(match.group(3)) if match.group(3) else None
        end_line = int(match.group(4)) if match.group(4) else None
        code_content = match.group(5).strip()
        
        return file_path, start_line, code_content
    
    return None, None, code_block


def parse_issue_block(issue_text: str) -> Dict:
    """
    解析单个问题块
    
    Args:
        issue_text: 问题块文本
    
    Returns:
        包含问题信息的字典
    """
    issue = {
        "title": "",
        "code_block": "",
        "file_path": None,
        "line_number": None,
        "risk_level": "",
        "description": "",
        "suggestion": "",
        "raw_text": issue_text
    }
    
    # 提取标题（#### 数字. 标题）
    title_match = re.search(r"####\s*\d+\.\s*(.+?)\n", issue_text)
    if title_match:
        issue["title"] = title_match.group(1).strip()
    
    # 提取代码块
    code_match = re.search(r"(```[\s\S]*?```)", issue_text)
    if code_match:
        issue["code_block"] = code_match.group(1)
        file_path, line_number, _ = parse_code_block(issue["code_block"])
        issue["file_path"] = file_path
        issue["line_number"] = line_number
    
    # 提取风险等级
    risk_match = re.search(r"\*\*风险等级\*\*[：:](\s*)(高|中|低)", issue_text)
    if risk_match:
        issue["risk_level"] = risk_match.group(2)
    
    # 提取问题描述
    desc_match = re.search(r"\*\*问题描述\*\*[：:](.+?)(?=\*\*建议\*\*|$)", issue_text, re.DOTALL)
    if desc_match:
        issue["description"] = desc_match.group(1).strip()
    
    # 提取建议
    suggest_match = re.search(r"\*\*建议\*\*[：:](.+?)(?=####|$)", issue_text, re.DOTALL)
    if suggest_match:
        issue["suggestion"] = suggest_match.group(1).strip()
    
    return issue


def parse_review_report(report_content: str) -> Tuple[List[Dict], str]:
    """
    解析代码审查报告，提取潜在问题和改进建议
    
    Args:
        report_content: 审查报告内容
    
    Returns:
        (潜在问题列表, 改进建议文本)
    """
    issues = []
    suggestions = ""
    
    # 提取潜在问题部分
    # 支持格式: "### [-] 潜在问题" 或 "### ⚠️ 潜在问题" 或 "### 潜在问题"
    issues_section_match = re.search(
        r"###\s*(?:\[-\]|⚠️)?\s*潜在问题([\s\S]*?)(?=###\s*(?:\[\*\]|💡)?\s*改进建议|###\s*📊|---\s*$|$)",
        report_content
    )
    
    if issues_section_match:
        issues_section = issues_section_match.group(1)
        # 分割各个问题块（以 #### 数字. 开头）
        issue_blocks = re.split(r"(?=####\s*\d+\.)", issues_section)
        for block in issue_blocks:
            block = block.strip()
            if block and re.match(r"####\s*\d+\.", block):
                issue = parse_issue_block(block)
                issues.append(issue)
    
    # 提取改进建议部分
    # 支持格式: "### [*] 改进建议" 或 "### 💡 改进建议" 或 "### 改进建议"
    suggestions_match = re.search(
        r"###\s*(?:\[\*\]|💡)?\s*改进建议([\s\S]*?)(?=###\s*📊|---\s*$|$)",
        report_content
    )
    
    if suggestions_match:
        suggestions = suggestions_match.group(1).strip()
    
    return issues, suggestions


def format_issue_comment(issue: Dict) -> str:
    """
    格式化问题为评论内容
    
    Args:
        issue: 问题字典
    
    Returns:
        格式化后的评论内容
    """
    comment_parts = []
    
    # 标题
    if issue["title"]:
        comment_parts.append(f"## ⚠️ {issue['title']}")
    
    # 代码块
    if issue["code_block"]:
        comment_parts.append(f"\n{issue['code_block']}\n")
    
    # 风险等级
    if issue["risk_level"]:
        risk_emoji = {"高": "🔴", "中": "🟡", "低": "🟢"}.get(issue["risk_level"], "⚪")
        comment_parts.append(f"**风险等级**：{risk_emoji} {issue['risk_level']}")
    
    # 问题描述
    if issue["description"]:
        comment_parts.append(f"\n**问题描述**：{issue['description']}")
    
    # 建议
    if issue["suggestion"]:
        comment_parts.append(f"\n**建议**：\n{issue['suggestion']}")
    
    comment_parts.append("\n---\n*此评论由自动化代码审查工具生成*")
    
    return "\n".join(comment_parts)


def format_suggestions_comment(suggestions: str) -> str:
    """
    格式化改进建议为评论内容
    
    Args:
        suggestions: 改进建议文本
    
    Returns:
        格式化后的评论内容
    """
    return f"""## 💡 改进建议

{suggestions}

---
*此评论由自动化代码审查工具生成*"""


def publish_review_comments(repo_owner: str, repo_name: str, pr_number: str, 
                           token: str, report_content: str) -> Tuple[int, int]:
    """
    发布代码审查评论
    
    Args:
        repo_owner: 仓库所有者
        repo_name: 仓库名称
        pr_number: PR 编号
        token: GitCode Token
        report_content: 审查报告内容
    
    Returns:
        (成功数, 失败数)
    """
    success_count = 0
    fail_count = 0
    
    # 解析审查报告
    issues, suggestions = parse_review_report(report_content)
    
    print(f"\n解析到 {len(issues)} 个潜在问题")
    
    # 发布每个问题的评论
    for i, issue in enumerate(issues, 1):
        print(f"\n处理问题 {i}/{len(issues)}: {issue['title']}")
        
        comment_body = format_issue_comment(issue)
        
        # 如果有文件路径和行号，发布行级评论
        if issue["file_path"] and issue["line_number"]:
            print(f"  -> 发布行级评论: {issue['file_path']}#L{issue['line_number']}")
            success = post_comment_to_gitcode(
                repo_owner, repo_name, pr_number, comment_body, token,
                path=issue["file_path"],
                position=issue["line_number"]
            )
        else:
            # 否则发布为整体评论
            print(f"  -> 发布整体评论（未找到文件路径或行号）")
            success = post_comment_to_gitcode(
                repo_owner, repo_name, pr_number, comment_body, token
            )
        
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    # 发布改进建议评论
    if suggestions:
        print(f"\n发布改进建议评论...")
        suggestions_comment = format_suggestions_comment(suggestions)
        success = post_comment_to_gitcode(
            repo_owner, repo_name, pr_number, suggestions_comment, token
        )
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    return success_count, fail_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="发布评论到 GitCode PR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 发布简单评论
  python3 pr-comment.py -c "这是一条评论"
  
  # 从文件读取评论
  python3 pr-comment.py -f comment.md
  
  # 解析审查报告并发布（潜在问题作为行级评论，改进建议作为整体评论）
  python3 pr-comment.py -f review_report.md --parse-report
  
  # 发布行级评论
  python3 pr-comment.py -c "问题描述" --path src/main.cj --position 20
"""
    )
    parser.add_argument("-c", "--comment", help="评论内容")
    parser.add_argument("-f", "--file", help="从文件读取评论内容")
    parser.add_argument("--parse-report", action="store_true", 
                        help="解析审查报告格式，自动拆分问题和建议发布")
    parser.add_argument("--path", help="文件路径（用于行级评论）")
    parser.add_argument("--position", type=int, help="代码行号（用于行级评论）")
    args = parser.parse_args()
    
    # 从环境变量获取 PR 信息
    owner = os.environ.get("REPO_OWNER")
    repo = os.environ.get("REPO_NAME")
    pr_num = os.environ.get("PR_NUMBER")
    token = os.environ.get("GITCODE_TOKEN")
    
    if not all([owner, repo, pr_num, token]):
        print("请设置 REPO_OWNER, REPO_NAME, PR_NUMBER, GITCODE_TOKEN 环境变量")
        sys.exit(1)
    
    # 获取评论内容
    content = None
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            sys.exit(1)
    elif args.comment:
        content = args.comment
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        print("请通过 -c/--comment 或 -f/--file 或管道提供评论内容")
        sys.exit(1)
    
    if not content or not content.strip():
        print("评论内容不能为空")
        sys.exit(1)
    
    content = content.strip()
    
    # 根据模式发布评论
    if args.parse_report:
        # 解析审查报告模式
        print("正在解析审查报告并发布评论...")
        success_count, fail_count = publish_review_comments(
            owner, repo, pr_num, token, content
        )
        print(f"\n发布完成：成功 {success_count} 条，失败 {fail_count} 条")
        sys.exit(0 if fail_count == 0 else 1)
    else:
        # 普通评论模式
        success = post_comment_to_gitcode(
            owner, repo, pr_num, content, token,
            path=args.path,
            position=args.position
        )
        sys.exit(0 if success else 1)