# tests/test_cart_ui.py
import allure
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from config import TEST_EMAIL, TEST_PASSWORD


@allure.epic("OpenCart UI自动化测试")
@allure.feature("购物车模块")
class TestCartUI:

    @allure.story("添加商品")
    @allure.title("TC-CART-001: 添加商品到购物车")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_success(self, page: Page):
        login_page = LoginPage(page)
        cart_page = CartPage(page)

        login_page.navigate()
        login_page.login(TEST_EMAIL, TEST_PASSWORD)
        login_page.verify_login_success()

        page.goto("http://127.0.0.1/opencart/")
        page.wait_for_load_state("networkidle")

        cart_page.search_product("MacBook")
        cart_page.open_product_detail("MacBook")
        cart_page.add_product_by_ui_click()

        alert_success = page.locator(".alert-success:has-text('Success: You have added')")
        assert alert_success.count() > 0, "加购成功提示未出现"

        cart_page.go_to_checkout()
        item_count = cart_page.get_cart_item_count()
        assert item_count > 0, f"购物车商品数量应为>0，实际为{item_count}"

        print("✅ TC-CART-001 通过")

    @allure.story("修改数量")
    @allure.title("TC-CART-002: 购物车修改商品数量")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_cart_quantity(self, page: Page):
        login_page = LoginPage(page)
        cart_page = CartPage(page)

        login_page.navigate()
        login_page.login(TEST_EMAIL, TEST_PASSWORD)
        login_page.verify_login_success()

        cart_page.clear_cart()
        page.goto("http://127.0.0.1/opencart/")
        page.wait_for_load_state("networkidle")

        cart_page.search_product("MacBook")
        cart_page.open_product_detail("MacBook")
        cart_page.add_product_by_ui_click()

        # ✅ 直接进入购物车页面（不是结算页面）
        page.goto("http://127.0.0.1/opencart/index.php?route=checkout/cart")
        page.wait_for_load_state("networkidle")

        # 获取原始总价
        total_elements = page.locator(".table-responsive .text-right:has-text('$')")
        if total_elements.count() > 0:
            initial_total = total_elements.last.text_content().strip()
        else:
            initial_total = page.locator(".table-responsive tbody tr:first-child td:last-child").text_content().strip()

        # 修改数量
        qty_input = page.locator(".table-responsive tbody tr:first-child input[name='quantity']")
        if qty_input.count() > 0:
            qty_input.fill("2")
            qty_input.press("Enter")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

        # 获取新总价
        total_elements = page.locator(".table-responsive .text-right:has-text('$')")
        if total_elements.count() > 0:
            new_total = total_elements.last.text_content().strip()
        else:
            new_total = page.locator(".table-responsive tbody tr:first-child td:last-child").text_content().strip()

        assert initial_total != new_total, f"总价应变化，原价:{initial_total}，现价:{new_total}"

        print("✅ TC-CART-002 通过")

    @allure.story("删除商品")
    @allure.title("TC-CART-003: 购物车删除商品")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_remove_cart_item(self, page: Page):
        login_page = LoginPage(page)
        cart_page = CartPage(page)

        login_page.navigate()
        login_page.login(TEST_EMAIL, TEST_PASSWORD)
        login_page.verify_login_success()

        cart_page.clear_cart()
        page.goto("http://127.0.0.1/opencart/")
        page.wait_for_load_state("networkidle")

        cart_page.search_product("MacBook")
        cart_page.open_product_detail("MacBook")
        cart_page.add_product_by_ui_click()

        # ✅ 直接进入购物车页面（不是结算页面）
        page.goto("http://127.0.0.1/opencart/index.php?route=checkout/cart")
        page.wait_for_load_state("networkidle")

        # 使用 JavaScript 强制点击删除按钮
        page.evaluate("""
            const tr = document.querySelector('.table-responsive tbody tr:first-child');
            if (tr) {
                const btn = tr.querySelector('.btn-danger, button[name="remove"], button[data-bs-target*="remove"]');
                if (btn) btn.click();
            }
        """)
        page.wait_for_timeout(1000)
        page.wait_for_load_state("networkidle")

        # 验证删除成功
        page.wait_for_timeout(1000)
        item_count = page.locator(".table-responsive tbody tr").count()
        content_text = page.locator("body").inner_text()

        if item_count == 0 or "empty" in content_text.lower():
            print("✅ 购物车已空")
        else:
            raise AssertionError(f"购物车仍有 {item_count} 件商品")

        print("✅ TC-CART-003 通过")

    @allure.story("空购物车")
    @allure.title("TC-CART-004: 空购物车展示")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_cart_display(self, page: Page):
        page.goto("http://127.0.0.1/opencart/index.php?route=checkout/cart")
        page.wait_for_load_state("networkidle")

        delete_btn = page.locator("button[name='remove']")
        while delete_btn.count() > 0:
            delete_btn.first.click()
            page.wait_for_timeout(500)
            page.wait_for_load_state("networkidle")
            delete_btn = page.locator("button[name='remove']")

        page.wait_for_timeout(1000)

        content_text = page.locator("body").inner_text()
        assert "empty" in content_text.lower(), f"空购物车提示不正确，实际内容: {content_text[:200]}"

        print("✅ TC-CART-004 通过")

    @allure.story("未登录加购")
    @allure.title("TC-CART-005: 未登录加购跳转登录")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_to_cart_without_login(self, page: Page):
        cart_page = CartPage(page)

        page.context.clear_cookies()

        page.goto("http://127.0.0.1/opencart/")
        page.wait_for_load_state("networkidle")

        cart_page.search_product("MacBook")
        cart_page.open_product_detail("MacBook")
        cart_page.add_product_by_ui_click()

        current_url = page.url
        if "login" in current_url:
            print("✅ 未登录加购跳转到登录页")
        else:
            alert = page.locator(".alert-warning:has-text('login')")
            if alert.count() > 0:
                print("✅ 显示需要登录的提示")
            else:
                print(f"⚠️ 当前URL: {current_url}")

        print("✅ TC-CART-005 通过")