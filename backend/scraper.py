import asyncio
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


async def get_campus_schedule():
    """
    异步课表抓取核心函数（已整理）
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # 打开登录页（建议使用学校主入口以处理 cookie/跳转）
            print("正在打开登录页面...")
            await page.goto("https://jwxt.nfu.edu.cn/jwglxt/xtgl/login_slogin.html")

            # 等待账号输入框出现
            print("等待账号框加载...")
            await page.wait_for_selector("#yhm", timeout=10000)

            # 输入账号与密码（使用 type 可设置 delay 模拟人工输入）
            print("正在输入账号密码...")
            await page.type("#yhm", "2320110098", delay=150)
            await page.type("#mm", "153624orhA", delay=150)

            # 等待短暂思考时间
            await page.wait_for_timeout(1000)

            # 点击登录
            print("点击登录...")
            try:
                await page.click("#dl", timeout=5000)
            except Exception:
                print("备选：通过按钮文本定位登录按钮")
                await page.click('button:has-text("登录")', timeout=5000)

            # 等待 10 秒，确保登录跳转或页面稳定（你要求的等待）
            print("等待 10 秒，确保登录跳转完成...")
            await page.wait_for_timeout(3000)

            # 打印当前 URL 便于调试
            print(f"当前页面 URL: {page.url}")

            # 展开信息查询 -> 点击个人课表查询
            print("展开信息查询菜单...")
            # 利用 Playwright 的 has-text 伪类
            await page.click('a.dropdown-toggle:has-text("信息查询")')
            
            print("点击个人课表查询...")
            await page.get_by_text("个人课表查询").click(timeout=5000)
            
            # 使用 get_by_text，它会自动查找包含“个人课表查询”文字的 <a> 标签
            # 这样你就避开了复杂的 onclick 逻辑
            target_link = page.get_by_role("link", name="个人课表查询")
            
            # 1. 触发点击动作，同时等待新页面产生
            async with page.context.expect_page() as new_page_info:
            # 模拟人工点击
                await page.get_by_role("link", name="个人课表查询").click()

            # 2. 获取这个新页面对象
            new_page = await new_page_info.value

            # 3. 非常重要：等待新页面完全加载
            await new_page.wait_for_load_state("networkidle")

            # 4. 以后所有的抓取动作（如查找课表表格）都要在 new_page 上进行
            # 比如：await new_page.wait_for_selector("#Table1")


            # TODO: 在这里解析课表表格并返回结果
            print("课表页面加载完成，开始抓取数据（TODO）")
            return ["登录流程测试结束"]

        except PlaywrightTimeoutError:
            print("错误：页面响应超时，可能网络不通或元素定位失效。")
            return ["抓取超时"]
        except Exception as e:
            print(f"发生错误: {e}")
            return [f"错误: {e}"]
        finally:
            await browser.close()


if __name__ == "__main__":
    result = asyncio.run(get_campus_schedule())
    print("结果:", result)
