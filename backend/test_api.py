#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试课表爬虫 API 的脚本
"""
import requests
import json
import asyncio
from scraper import get_campus_schedule

# API 地址
API_URL = "http://127.0.0.1:8000/api/schedule"

def test_api():
    """测试 API 接口"""
    print("=" * 60)
    print("测试课表爬虫 API")
    print("=" * 60)
    
    # 测试数据
    test_data = {
        "username": "2320110098",
        "password": "153624orhA"
    }
    
    print(f"\n📤 发送请求到: {API_URL}")
    print(f"📝 请求参数: {test_data}")
    print("\n⏳ 正在爬虫中，请稍候（首次运行会比较慢）...\n")
    
    try:
        response = requests.post(API_URL, json=test_data, timeout=120)
        
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功！")
            print(f"\n响应数据:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 如果有数据，保存到文件
            if "data" in result and result["data"]:
                save_path = "api_schedule_result.json"
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(result["data"], f, ensure_ascii=False, indent=4)
                print(f"\n💾 数据已保存到: {save_path}")
        else:
            print(f"❌ 请求失败！")
            print(f"响应内容: {response.text}")
    
    except requests.exceptions.Timeout:
        print("❌ 请求超时（超过 120 秒）")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("请确保后端已启动: python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


async def test_scraper_directly():
    """直接测试爬虫函数"""
    print("\n" + "=" * 60)
    print("直接测试爬虫函数（无 API）")
    print("=" * 60)
    
    print("\n⏳ 正在爬虫中...\n")
    
    result = await get_campus_schedule(
        username="2320110098",
        password="153624orhA"
    )
    
    if isinstance(result, dict) and "error" in result:
        print(f"❌ 爬虫失败: {result['error']}")
    else:
        print(f"✅ 爬虫成功！获得 {len(result)} 条课表")
        print(f"\n前 3 条数据:")
        for i, item in enumerate(result[:3], 1):
            print(f"\n  第 {i} 条:")
            print(f"    {json.dumps(item, ensure_ascii=False, indent=6)}")
        
        # 保存数据
        save_path = "scraper_result.json"
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"\n💾 完整数据已保存到: {save_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # 测试 API
        test_api()
    else:
        # 默认：直接测试爬虫
        asyncio.run(test_scraper_directly())
        
        print("\n" + "=" * 60)
        print("💡 提示：要测试 API，运行: python test_api.py api")
        print("=" * 60)
