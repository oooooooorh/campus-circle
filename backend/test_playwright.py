#!/usr/bin/env python
# 测试Playwright浏览器安装状态
import subprocess
import sys
import os

def check_browser_status():
    """检查Playwright浏览器状态"""
    print("=" * 60)
    print("Playwright 浏览器状态检查")
    print("=" * 60)
    
    playwright_path = os.path.expanduser(r"~\AppData\Local\ms-playwright")
    
    if os.path.exists(playwright_path):
        print(f"\n✓ Playwright 目录存在: {playwright_path}")
        browsers = os.listdir(playwright_path)
        print(f"已安装的浏览器: {browsers}")
    else:
        print(f"\n✗ Playwright 目录不存在: {playwright_path}")
    
    print("\n尝试安装 Chromium...")
    print("-" * 60)
    
    try:
        # 运行 playwright install chromium
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=False,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("\n✓ Chromium 安装成功！")
            return True
        else:
            print(f"\n✗ 安装失败，返回码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ 安装超时（超过5分钟）")
        return False
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        return False

if __name__ == "__main__":
    success = check_browser_status()
    sys.exit(0 if success else 1)
