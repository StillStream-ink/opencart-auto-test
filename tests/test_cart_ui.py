import allure
from playwright.sync_api import Page
from pages.cart_page import CartPage
from config import BASE_URL


@allure.epic("OpenCart UI自动化测试")
@allure.feature("购物车模块")
class TestCartUI:

    @allure.story("添加商品")
    @allure.title("TC-CART-001: 添加商品到购物车")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_success(self, logged_in_page: Page):
        page = logged_in_page
        cart_page = CartPage(page)

        with allure.step("搜索并打开商品详情"):
            page.goto(f"{BASE_URL}/")
            page.wait_for_load_state("networkidle")
            cart_page.search_product("MacBook")
            cart_page.open_product_detail("MacBook")

        with allure.step("加入购物车并校验提示"):
            cart_page.add_product_by_ui_click()
            alert_success = page.locator(".alert-success:has-text('Success: You have added')")
            assert alert_success.count() > 0, "加购成功提示未出现"

        with allure.step("进入购物车校验商品存在"):
            cart_page.go_to_checkout()
            item_count = cart_page.get_cart_item_count()
            assert item_count > 0, f"购物车商品数量应为>0，实际为{item_count}"

    @allure.story("修改数量")
    @allure.title("TC-CART-002: 购物车修改商品数量")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_cart_quantity(self, logged_in_page: Page):
        page = logged_in_page
        cart_page = CartPage(page)

        with allure.step("准备：加一件商品"):
            cart_page.clear_cart()
            page.goto(f"{BASE_URL}/")
            page.wait_for_load_state("networkidle")
            cart_page.search_product("MacBook")
            cart_page.open_product_detail("MacBook")
            cart_page.add_product_by_ui_click()
            page.goto(f"{BASE_URL}/index.php?route=checkout/cart")
            page.wait_for_load_state("networkidle")

        with allure.step("归一化：数量设为 1"):
            cart_page.update_cart_quantity(1, 1)
            qty_input = page.locator(".table-responsive tbody tr:first-child input[name='quantity']")
            assert qty_input.get_attribute("value") == "1", "初始数量应该是1"

        with allure.step("修改：数量设为 2 并校验"):
            cart_page.update_cart_quantity(1, 2)
            qty_input = page.locator(".table-responsive tbody tr:first-child input[name='quantity']")
            assert qty_input.get_attribute("value") == "2", "新数量应该是2"

    @allure.story("删除商品")
    @allure.title("TC-CART-003: 购物车删除商品")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_remove_cart_item(self, logged_in_page: Page):
        page = logged_in_page
        cart_page = CartPage(page)

        cart_page.clear_cart()
        page.goto(f"{BASE_URL}/")
        page.wait_for_load_state("networkidle")
        cart_page.search_product("MacBook")
        cart_page.open_product_detail("MacBook")
        cart_page.add_product_by_ui_click()
        page.goto(f"{BASE_URL}/index.php?route=checkout/cart")
        page.wait_for_load_state("networkidle")

        with allure.step("删除唯一商品"):
            cart_page.remove_cart_item(1)
            page.wait_for_timeout(1000)

        with allure.step("校验购物车为空"):
            item_count = page.locator(".table-responsive tbody tr").count()
            content_text = page.locator("body").inner_text()
            assert item_count == 0 or "empty" in content_text.lower(), \
                f"购物车仍有 {item_count} 件商品"

    @allure.story("空购物车")
    @allure.title("TC-CART-004: 空购物车展示")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_cart_display(self, page: Page):
        page.goto(f"{BASE_URL}/index.php?route=checkout/cart")
        page.wait_for_load_state("networkidle")
        content_text = page.locator("body").inner_text()
        assert "empty" in content_text.lower(), \
            f"空购物车提示不正确，实际内容: {content_text[:200]}"

    @allure.story("未登录加购")
    @allure.title("TC-CART-005: 未登录加购（游客加购或跳转登录）")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_to_cart_without_login(self, page: Page):
        cart_page = CartPage(page)
        page.context.clear_cookies()
        page.goto(f"{BASE_URL}/")
        page.wait_for_load_state("networkidle")
        cart_page.search_product("MacBook")
        cart_page.open_product_detail("MacBook")
        cart_page.add_product_by_ui_click()

        add_success = page.locator(".alert-success:has-text('Success')").count() > 0
        login_redirect = "login" in page.url
        assert add_success or login_redirect, \
            f"未登录加购既没成功也没跳转登录，URL: {page.url}"