#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接启动 Uvicorn 服务器的脚本
"""
import os
import sys
import uvicorn

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 直接调用 uvicorn.run()
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False
    )
