#!/usr/bin/env python3
"""
飞书课程报告链接生成器
自动读取飞书表格，为每条记录生成报告链接并回填到"報告鏈接"字段
"""

import requests
import json
import os

# 飞书配置
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', 'cli_a971a71ab0395cce')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', 'T94yU3Og4QHiWxqmw4DNreSCipBmlJf7')
BITABLE_APP_TOKEN = 'DOK5bKaDtaJAnpsp3UZcuibRnFf'
TABLE_ID = 'tblfigiNW09OkXU9'

# GitHub Pages 报告地址（静态 HTML 格式）
REPORT_BASE_URL = 'https://wwzz168.github.io/kechengbaogao'

def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {'Content-Type': 'application/json'}
    data = {
        'app_id': FEISHU_APP_ID,
        'app_secret': FEISHU_APP_SECRET
    }

    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()

    if result.get('code') != 0:
        raise Exception(f"获取 token 失败: {result}")

    return result['tenant_access_token']

def get_all_records(token):
    """获取表格所有记录"""
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/records'
    headers = {'Authorization': f'Bearer {token}'}

    all_records = []
    page_token = None

    while True:
        params = {'page_size': 500}
        if page_token:
            params['page_token'] = page_token

        resp = requests.get(url, headers=headers, params=params)
        result = resp.json()

        if result.get('code') != 0:
            raise Exception(f"获取记录失败: {result}")

        items = result['data'].get('items', [])
        all_records.extend(items)

        page_token = result['data'].get('page_token')
        if not page_token:
            break

    return all_records

def update_record_link(token, record_id, link):
    """更新记录的報告鏈接字段"""
    url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'fields': {
            '報告鏈接': {
                'link': link,
                'text': '查看报告'
            }
        }
    }

    resp = requests.put(url, headers=headers, json=data)
    result = resp.json()

    if result.get('code') != 0:
        raise Exception(f"更新记录失败: {result}")

    return True

def check_record_complete(record):
    """检查记录是否有完整数据（高光视频和分析非必填）"""
    fields = record.get('fields', {})
    required_fields = ['學生姓名', '課程名稱', '上課時間', '课程重点', '本节课核心',
                       '答題正確率', '答題總數', '答題正確數', '答错数', '課程知識點',
                       '答题情况评价', '老师点评', '主講老師', '下节课预告', '下节课预习建议']
    for field in required_fields:
        if not fields.get(field):
            return False
    return True

def main():
    print("=" * 50)
    print("飞书课程报告链接生成器")
    print("=" * 50)

    try:
        # 1. 获取 token
        print("\n正在获取飞书访问令牌...")
        token = get_tenant_access_token()
        print("✓ Token 获取成功")

        # 2. 获取所有记录
        print("\n正在读取表格记录...")
        records = get_all_records(token)
        print(f"✓ 共读取到 {len(records)} 条记录")

        # 3. 处理每条记录
        print("\n正在处理记录...")
        success_count = 0
        skip_count = 0
        error_count = 0

        for record in records:
            record_id = record['record_id']
            fields = record.get('fields', {})
            student_name = fields.get('學生姓名', '未知')

            # 检查数据是否完整
            if not check_record_complete(record):
                print(f"  ⚠ {student_name} - 数据不完整，跳过")
                skip_count += 1
                continue

            # 生成报告链接（新格式：静态 HTML）
            report_link = f"{REPORT_BASE_URL}/{record_id}.html"

            try:
                # 更新记录
                update_record_link(token, record_id, report_link)
                print(f"  ✓ {student_name} - 链接已更新: {report_link}")
                success_count += 1
            except Exception as e:
                print(f"  ✗ {student_name} - 更新失败: {str(e)}")
                error_count += 1

        # 4. 输出结果
        print("\n" + "=" * 50)
        print("处理完成！")
        print(f"  成功生成: {success_count} 条")
        print(f"  跳过处理: {skip_count} 条")
        print(f"  处理失败: {error_count} 条")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ 程序运行出错: {str(e)}")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
