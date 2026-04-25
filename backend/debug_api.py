#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug API endpoint issue
"""

import sys
import asyncio
import logging

# Configure logging with file output to capture full error
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

from scraper import get_campus_schedule
from schemas import LoginInfo

async def test():
    logger.info("Starting API test...")
    try:
        logger.info("Calling get_campus_schedule...")
        result = await get_campus_schedule("2320110098", "153624orhA")
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        result = asyncio.run(test())
        print(f"✅ Test passed, got {len(result) if isinstance(result, list) else '?'} courses")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Check api_debug.log for details")
