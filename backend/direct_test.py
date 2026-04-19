#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试FastAPI异步调用，不通过HTTP
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_direct_call():
    """直接测试爬虫函数"""
    logger.info("=== 直接调用爬虫（模拟FastAPI异步上下文） ===")
    
    try:
        from scraper import get_campus_schedule
        
        logger.info("开始爬虫调用...")
        result = await get_campus_schedule("2320110098", "153624orhA")
        
        logger.info(f"爬虫返回类型: {type(result).__name__}")
        
        if isinstance(result, dict) and "error" in result:
            logger.error(f"爬虫返回错误: {result['error']}")
        elif isinstance(result, list):
            logger.info(f"爬虫返回课程数: {len(result)}")
            if result:
                first = result[0]
                logger.info(f"首课程: {first.get('kcmc', '?')}")
        else:
            logger.warning(f"未预期的返回类型: {type(result)}")
            
    except Exception as e:
        logger.error(f"爬虫调用异常: {e}", exc_info=True)
        import traceback
        traceback.print_exc()

async def test_api_endpoint():
    """测试 API 端点"""
    logger.info("\n=== 测试 FastAPI 端点 ===")
    
    try:
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        logger.info("发送 POST 请求到 /api/schedule...")
        response = client.post(
            "/api/schedule",
            json={"username": "2320110098", "password": "153624orhA"}
        )
        
        logger.info(f"响应状态码: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            logger.info(f"成功! 课程数: {result.get('count')}")
        else:
            logger.error(f"错误: {result}")
            
    except Exception as e:
        logger.error(f"API 测试异常: {e}", exc_info=True)


async def main():
    logger.info("开始诊断...")
    
    # 测试直接调用
    await test_direct_call()
    
    # 测试API端点（如果testclient可用）
    try:
        await test_api_endpoint()
    except Exception as e:
        logger.warning(f"无法测试API端点（可能是httpx缺失）: {e}")


if __name__ == "__main__":
    asyncio.run(main())
