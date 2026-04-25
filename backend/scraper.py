import asyncio
import os
import json
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# 配置文件输出路径（可选，用于调试）
OUTPUT_DIR = "schedule_logs"


def save_schedule_to_file(data, filename=None):
    """
    保存课表数据到 JSON 文件，防止乱码
    
    Args:
        data: 课表数据列表
        filename: 文件名（可选）
    """
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        if filename is None:
            filename = f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        save_path = os.path.join(OUTPUT_DIR, filename)
        
        # 关键：指定 encoding='utf-8' 和 ensure_ascii=False
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 课表数据已保存到: {save_path}")
        return save_path
    except Exception as e:
        print(f"⚠️ 保存课表文件失败: {e}")
        return None


async def get_campus_schedule(context, username: str = "2320110098", password: str = "153624orhA", save_to_file: bool = False, timeout: int = 120):
    """
    异步课表爬虫函数 (依赖外部传入 BrowserContext)
    """
    intercepted_schedule_data = []
    
    if not username or not password:
        return {"error": "账号密码不能为空"}

    async def handle_response(response):
        """网络响应拦截回调"""
        try:
            if "xskbcx_cxXsgrkb" in response.url and response.request.method == "POST":
                print(f"📡 拦截到目标接口响应: {response.url}")
                json_data = await response.json()
                if "kbList" in json_data:
                    kb_list = json_data["kbList"]
                    print(f"🎉 成功提取到 kbList！共有 {len(kb_list)} 节课的信息。")
                    intercepted_schedule_data.extend(kb_list)
        except Exception:
            pass

    page = await context.new_page()

    try:
        # 1. 打开登录页 (设置超时防止卡死)
        print(f"正在打开登录页面...")
        await page.goto("https://jwxt.nfu.edu.cn/jwglxt/xtgl/login_slogin.html", timeout=30000)
        await page.wait_for_selector("#yhm", timeout=10000)

        # 2. 输入账号密码
        print(f"正在输入账号密码...")
        await page.type("#yhm", username, delay=50)
        await page.type("#mm", password, delay=50)

        print("点击登录...")
        try:
            await page.click("#dl", timeout=5000)
        except Exception:
            await page.click('button:has-text("登录")', timeout=5000)

        # 等待登录跳转完成
        print("等待登录跳转完成...")
        await page.wait_for_timeout(3000)
        print(f"当前页面 URL: {page.url}")

        # 检查登录是否失败（简单判断）
        if "login_slogin.html" in page.url:
            return {"error": "登录失败，请检查账号密码"}

        # 3. 展开信息查询菜单
        print("展开信息查询菜单...")
        await page.click('a.dropdown-toggle:has-text("信息查询")')
        
        print("准备点击个人课表查询，并挂载网络监听器...")
        
        # 4. 触发新页面，并获取新页面的引用
        async with context.expect_page() as new_page_info:
            await page.get_by_role("link", name="个人课表查询").click()

        new_page = await new_page_info.value
        
        # 🚨 核心：在新页面上挂载响应拦截器
        new_page.on("response", handle_response)
        print("👂 监听器已在新页面就位，等待网络请求...")

        # 等待新页面的网络请求完全结束
        await new_page.wait_for_load_state("networkidle")
        
        # 再等待一会儿让最后的数据处理完毕
        print("⏳ 等待 2 秒钟，确保接口数据提取完成...")
        await new_page.wait_for_timeout(2000)

        # 5. 返回拦截到的数据
        if intercepted_schedule_data:
            print(f"✅ 成功抓取 {len(intercepted_schedule_data)} 条课表记录")
            if save_to_file:
                save_schedule_to_file(intercepted_schedule_data)
            return intercepted_schedule_data
        else:
            print("⚠️ 未抓取到任何数据。")
            return {"error": "未拦截到课表数据"}

    except PlaywrightTimeoutError:
        print("❌ 错误：页面响应超时。")
        return {"error": "抓取超时（可能是网络问题）"}
    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}"
        print(f"❌ 发生错误: {error_detail}")
        return {"error": error_detail}
    finally:
        await page.close()


if __name__ == "__main__":
    # 配置标准输出为 UTF-8 编码（Windows 兼容性）
    import sys
    import io
    import json
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    async def run_test(username, password, save_to_file):
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            try:
                return await get_campus_schedule(context, username, password, save_to_file)
            finally:
                await context.close()
                await browser.close()
                
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
        try:
            result = asyncio.run(run_test(username, password, save_to_file=False))
            print("JSON_OUTPUT_START")
            print(json.dumps(result, ensure_ascii=False))
            print("JSON_OUTPUT_END")
            sys.exit(0)
        except Exception as e:
            print("JSON_OUTPUT_START")
            print(json.dumps({"error": str(e) if str(e) else "Playwright Error"}, ensure_ascii=False))
            print("JSON_OUTPUT_END")
            sys.exit(1)
    else:
        print("-" * 50)
        print("开始测试课表爬虫...")
        print("提示：请修改 username 和 password 参数后再运行")
        print("-" * 50)
        try:
            # 本地测试：使用默认账号或修改以下参数
            result = asyncio.run(run_test(
                username="2320110098",
                password="153624orhA",
                save_to_file=True  # 保存结果到文件
            ))
            
            if isinstance(result, dict) and "error" in result:
                print(f"❌ 失败: {result['error']}")
            else:
                print(f"✅ 成功: 获得 {len(result) if isinstance(result, list) else 0} 条课表")
                # 打印第一条课程的详细信息（UTF-8 测试）
                if isinstance(result, list) and len(result) > 0:
                    first_course = result[0]
                    print(f"\n【首条课程示例】")
                    print(f"  课程名称: {first_course.get('kcmc', 'N/A')}")
                    print(f"  教师: {first_course.get('xm', 'N/A')}")
                    print(f"  地点: {first_course.get('cdmc', 'N/A')}")
        except Exception as e:
            import traceback
            print(f"❌ 异常: {e}")
            traceback.print_exc()

