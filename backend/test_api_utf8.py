#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 API 端点，验证 UTF-8 编码正确性
"""

import sys
import io
# 确保标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import urllib.request
import json
import time

def test_api():
    """测试 /api/schedule 端点"""
    print("\n" + "="*60)
    print("🧪 API UTF-8 编码测试")
    print("="*60 + "\n")
    
    api_url = 'http://127.0.0.1:8000/api/schedule'
    
    # 准备请求
    payload = {
        'username': '2320110098',
        'password': '153624orhA'
    }
    
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json; charset=utf-8'
        }
    )
    
    try:
        print(f"📡 请求 API: {api_url}")
        print(f"📝 请求体: {json.dumps(payload, ensure_ascii=False)}\n")
        
        start_time = time.time()
        resp = urllib.request.urlopen(req, timeout=120)
        elapsed = time.time() - start_time
        
        # 读取响应
        response_data = resp.read()
        result = json.loads(response_data.decode('utf-8'))
        
        print(f"✅ API 响应成功！（耗时 {elapsed:.2f}s）\n")
        print(f"📊 响应信息:")
        print(f"   状态: {result.get('status')}")
        print(f"   课程数: {result.get('count')}")
        
        if result.get('data') and isinstance(result['data'], list):
            print(f"\n📚 课程样本（前3条）:")
            for i, course in enumerate(result['data'][:3], 1):
                print(f"\n   【课程 {i}】")
                print(f"   课程名: {course.get('kcmc', 'N/A')}")
                print(f"   教师: {course.get('xm', 'N/A')}")
                print(f"   地点: {course.get('cdmc', 'N/A')}")
                print(f"   星期: {course.get('xqjmc', 'N/A')}")
                print(f"   节次: {course.get('jc', 'N/A')}")
        
        print(f"\n✨ UTF-8 编码测试: ✅ 通过")
        print("="*60 + "\n")
        return True
        
    except urllib.error.HTTPError as e:
        print(f"❌ API 错误: HTTP {e.code}\n")
        error_content = e.read().decode('utf-8')
        print(f"📋 错误详情:")
        print(f"   {error_content}")
        print("\n❌ UTF-8 编码测试: ❌ 失败")
        print("="*60 + "\n")
        return False
        
    except Exception as e:
        print(f"❌ 发生异常: {e}\n")
        import traceback
        traceback.print_exc()
        print("\n❌ UTF-8 编码测试: ❌ 异常")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
