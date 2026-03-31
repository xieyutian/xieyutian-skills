#!/usr/bin/env python3
"""
生成 GitCode API 文档索引文件
"""

import os
import re
import json
from pathlib import Path

# 目录映射
CATEGORY_MAP = {
    'openapi-intro': {
        'name': 'OpenAPI入门',
        'description': 'OpenAPI 使用入门和认证说明',
        'keywords': ['入门', '认证', 'access_token', 'api', '快速开始']
    },
    'repositories': {
        'name': '仓库',
        'description': '仓库相关 API，包括创建、删除、获取仓库信息、文件操作等',
        'keywords': ['仓库', 'repository', 'repo', '项目', '文件', 'fork', 'star', 'watch']
    },
    'branch': {
        'name': '分支',
        'description': '分支相关 API，包括创建、删除、获取分支信息、保护分支等',
        'keywords': ['分支', 'branch', '保护分支', 'branch protection']
    },
    'issues': {
        'name': 'Issue',
        'description': 'Issue 相关 API，包括创建、更新、获取、评论 Issue 等',
        'keywords': ['issue', '问题', '工单', '评论', 'label', '标签']
    },
    'pull-requests': {
        'name': 'Pull Request',
        'description': 'Pull Request 相关 API，包括创建、合并、获取、评论 PR 等',
        'keywords': ['pr', 'pull request', '合并请求', 'merge', 'review', '审查']
    },
    'search': {
        'name': '搜索',
        'description': '搜索相关 API，包括搜索仓库、用户、Issue 等',
        'keywords': ['搜索', 'search', '查找', 'query']
    },
    'users': {
        'name': '用户',
        'description': '用户相关 API，包括获取用户信息、更新资料、关注等',
        'keywords': ['用户', 'user', '个人资料', 'profile', '关注', 'follower']
    },
    'organizations': {
        'name': '组织',
        'description': '组织相关 API，包括创建、管理组织等',
        'keywords': ['组织', 'organization', 'org', '团队']
    },
    'enterprise': {
        'name': '企业',
        'description': '企业相关 API，包括企业管理、统计等',
        'keywords': ['企业', 'enterprise', '统计', 'statistics']
    },
    'webhooks': {
        'name': 'Webhook',
        'description': 'Webhook 相关 API，包括创建、管理 Webhook 等',
        'keywords': ['webhook', '钩子', '回调', 'callback', '事件']
    },
    'labels': {
        'name': '标签',
        'description': '标签相关 API，包括创建、更新、删除标签等',
        'keywords': ['标签', 'label', 'issue标签']
    },
    'milestone': {
        'name': '里程碑',
        'description': '里程碑相关 API，包括创建、更新、删除里程碑等',
        'keywords': ['里程碑', 'milestone', '版本', '计划']
    },
    'member': {
        'name': '成员',
        'description': '成员相关 API，包括添加、删除成员等',
        'keywords': ['成员', 'member', '协作者', 'collaborator', '权限']
    },
    'commit': {
        'name': '提交',
        'description': '提交相关 API，包括获取提交信息、比对提交等',
        'keywords': ['提交', 'commit', 'diff', '比较', '变更']
    },
    'release': {
        'name': '发布',
        'description': '发布相关 API，包括创建、更新、删除发布版本等',
        'keywords': ['发布', 'release', '版本', 'version']
    },
    'tag': {
        'name': 'Tag',
        'description': '标签相关 API，包括创建、获取、删除标签等',
        'keywords': ['标签', 'tag', '版本']
    },
    'dashboard': {
        'name': '仪表盘',
        'description': '仪表盘相关 API，包括获取动态、通知等',
        'keywords': ['仪表盘', 'dashboard', '动态', 'activity', '通知']
    },
    'ai-hub': {
        'name': 'AI Hub',
        'description': 'AI Hub 相关 API，包括文本生成、图像识别等 AI 功能',
        'keywords': ['ai', '人工智能', '文本生成', '图像', '语音', '识别']
    },
    'oauth': {
        'name': 'OAuth',
        'description': 'OAuth 2.0 相关 API，包括授权、获取 token 等',
        'keywords': ['oauth', '授权', '认证', 'token', 'access_token']
    },
    'changelog': {
        'name': '变更日志',
        'description': 'API 变更日志，记录 API 的更新历史',
        'keywords': ['变更', 'changelog', '更新', '历史', '版本']
    }
}

def extract_api_info(file_path):
    """从 API 文档中提取信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    # 提取标题
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    name = title_match.group(1) if title_match else Path(file_path).stem

    # 提取 API 端点
    method_match = re.search(r'\*\*方法:\*\* `(\w+)`', content)
    endpoint_match = re.search(r'\*\*端点:\*\* `([^`]+)`', content)

    api_endpoint = None
    if method_match and endpoint_match:
        endpoint_path = endpoint_match.group(1)
        # 提取相对路径
        if 'api.gitcode.com/api/v5' in endpoint_path:
            endpoint_path = endpoint_path.replace('https://api.gitcode.com/api/v5', '')
        api_endpoint = {
            'method': method_match.group(1),
            'path': endpoint_path
        }

    # 生成关键词
    keywords = []
    # 从名称提取关键词
    name_keywords = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', name)
    keywords.extend(name_keywords)

    # 添加常见操作关键词
    if '创建' in name or '新建' in name:
        keywords.extend(['创建', '新建', 'create'])
    if '获取' in name or '查询' in name:
        keywords.extend(['获取', '查询', 'get', 'list'])
    if '更新' in name or '修改' in name:
        keywords.extend(['更新', '修改', 'update', 'edit'])
    if '删除' in name:
        keywords.extend(['删除', 'delete', 'remove'])
    if '合并' in name:
        keywords.extend(['合并', 'merge'])

    # 唯一化关键词
    keywords = list(set(keywords))

    # 生成 ID
    category = Path(file_path).parent.name
    doc_id = f"{category}-{Path(file_path).stem}"

    return {
        'id': doc_id,
        'name': name,
        'path': f"references/api-docs/{category}/{Path(file_path).name}",
        'keywords': keywords,
        'apiEndpoint': api_endpoint,
        'summary': f"{name}的 API 文档",
        'category': category
    }

def generate_index(base_path):
    """生成索引文件"""
    index = {
        'version': '1.0.0',
        'lastUpdated': '2026-03-31',
        'baseUrl': 'https://api.gitcode.com/api/v5',
        'totalDocs': 0,
        'categories': {}
    }

    docs_path = Path(base_path) / 'references' / 'api-docs'

    for category_dir in docs_path.iterdir():
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name

        if category_name not in CATEGORY_MAP:
            print(f"Warning: Unknown category {category_name}")
            category_info = {
                'name': category_name,
                'description': f"{category_name}相关 API",
                'keywords': [category_name]
            }
        else:
            category_info = CATEGORY_MAP[category_name]

        index['categories'][category_name] = {
            'name': category_info['name'],
            'description': category_info['description'],
            'keywords': category_info['keywords'],
            'docs': []
        }

        for doc_file in category_dir.iterdir():
            if not doc_file.name.endswith('.md'):
                continue

            doc_info = extract_api_info(str(doc_file))
            if doc_info:
                doc_info['category'] = category_name
                doc_info['path'] = f"references/api-docs/{category_name}/{doc_file.name}"
                index['categories'][category_name]['docs'].append(doc_info)
                index['totalDocs'] += 1

    return index

def main():
    # 使用绝对路径
    base_path = Path(__file__).parent.parent
    index = generate_index(str(base_path))

    # 保存索引文件
    output_path = Path(base_path) / 'references' / 'index.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"索引文件已生成: {output_path}")
    print(f"共 {index['totalDocs']} 个文档")

    # 打印每个分类的文档数量
    for cat, data in index['categories'].items():
        print(f"  {cat}: {len(data['docs'])} 个文档")

if __name__ == '__main__':
    main()