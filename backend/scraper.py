import asyncio
import os
import json
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


async def get_campus_schedule():
    """
    异步课表抓取核心函数（已整理）
    拦截教务系统的 API 接口返回的纯净 JSON 数据
    """
    intercepted_schedule_data = []

    async def handle_response(response):
        """
        网络响应捕获回调
        """
        try:
            # 过滤条件：匹配获取个人课表的 API
            if "xskbcx_cxXsgrkb" in response.url and response.request.method == "POST":
                print(f"📡 拦截到目标接口响应: {response.url}")
                json_data = await response.json()
                
                if "kbList" in json_data:
                    kb_list = json_data["kbList"]
                    print(f"🎉 成功提取到 kbList！共有 {len(kb_list)} 节课的信息。")
                    intercepted_schedule_data.extend(kb_list)
        except Exception as e:
            # 忽略非JSON或无法解析的响应
            pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 1. 打开登录页
            print("正在打开登录页面...")
            await page.goto("https://jwxt.nfu.edu.cn/jwglxt/xtgl/login_slogin.html")
            await page.wait_for_selector("#yhm", timeout=10000)

            # 2. 输入账号密码
            print("正在输入账号密码...")
            await page.type("#yhm", "2320110098", delay=50)
            await page.type("#mm", "153624orhA", delay=50)

            print("点击登录...")
            try:
                await page.click("#dl", timeout=5000)
            except Exception:
                await page.click('button:has-text("登录")', timeout=5000)

            # 等待登录跳转完成
            print("等待登录跳转完成...")
            await page.wait_for_timeout(3000)
            print(f"当前页面 URL: {page.url}")

            # 3. 展开信息查询菜单
            print("展开信息查询菜单...")
            await page.click('a.dropdown-toggle:has-text("信息查询")')
            
            print("准备点击个人课表查询，并挂载网络监听器...")
            
            # 4. 触发新页面，并获取新页面的引用
            async with page.context.expect_page() as new_page_info:
                await page.get_by_role("link", name="个人课表查询").click()

            new_page = await new_page_info.value
            
            # 🚨 核心：在新页面上挂载响应拦截器
            new_page.on("response", handle_response)
            print("👂 监听器已在新页面就位，等待网络请求...")

            # 等待新页面的网络请求完全结束
            await new_page.wait_for_load_state("networkidle")
            
            # 再等待一会儿让最后的数据处理完毕
            print("⏳ 等待 3 秒钟，确保接口数据提取完成...")
            await new_page.wait_for_timeout(3000)

            # 5. 分析处理保存拦截到的数据
            if intercepted_schedule_data:
                # 存为本地文件
                save_path = os.path.join(os.path.dirname(__file__), "my_schedule.json")
                try:
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(intercepted_schedule_data, f, ensure_ascii=False, indent=4)
                    print(f"💾 完美！课表数据已提取并保存至: {save_path}")
                except Exception as e:
                    print(f"保存文件出错: {e}")
                
                # 直接返回 JSON 字符串给调用方（API 可直接使用）
                return json.dumps(intercepted_schedule_data, ensure_ascii=False)
            else:
                print("⚠️ 未抓取到任何数据。")
                return json.dumps({"error": "未拦截到课表数据"}, ensure_ascii=False)

        except PlaywrightTimeoutError:
            print("❌ 错误：页面响应超时。")
            return json.dumps({"error": "抓取超时"}, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            return json.dumps({"error": f"内部错误: {e}"}, ensure_ascii=False)
        finally:
            await browser.close()


if __name__ == "__main__":
    print("-" * 50)
    print("开始抓取个人课表数据...")
    try:
        # 在脚本本地执行时，将直接获取 JSON 并打印
        result_json = asyncio.run(get_campus_schedule())
        # 简化输出结果展示
        print(f"抓取结果长度: {len(result_json)} 字符")
        print("-" * 50)
        # 如果你想在控制台看具体JSON内容，可以把下面这行注释取消：
        # print("完整 JSON 内容:", result_json)
    except Exception as e:
        print(f"\n执行异常，请检查环境: {e}")

