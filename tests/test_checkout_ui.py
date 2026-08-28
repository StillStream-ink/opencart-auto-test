import allure
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from config import TEST_EMAIL, TEST_PASSWORD


@allure.epic("OpenCart前台电商系统")
@allure.feature("结算下单模块")
class TestCheckoutUI:

    @allure.epic("OpenCart前台电商系统")
    @allure.feature("结算下单模块")
    @allure.story("正向完整结算流程")
    @allure.title("TC-UI-CHECKOUT-001：登录-搜索商品-加购-结算下单正向流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试步骤：用户登录→搜索MacBook商品→加入购物车→进入结算页→选择地址、配送、支付方式，完成订单提交")
    def test_checkout_success(self, page: Page):
        login_page = LoginPage(page)
        checkout_page = CheckoutPage(page)
        cart_page = CartPage(page)

        with allure.step("1.打开网站，执行账号登录"):
            login_page.navigate()
            login_page.login(TEST_EMAIL, TEST_PASSWORD)
            login_page.verify_login_success()   # 确保登录成功

        with allure.step("2.搜索商品：MacBook，进入商品详情页"):
            cart_page.search_product("MacBook")
            cart_page.open_product_detail("MacBook")

        with allure.step("3.商品加入购物车，前往结算页面"):
            cart_page.add_product_by_ui_click()
            cart_page.go_to_checkout()

        with allure.step("4.结算页面填写收货地址并确认地址"):
            checkout_page.fill_address(
                firstname="test",
                lastname="user",
                address="123 Main Street",
                city="London",
                postcode="SW1A 1AA"
            )

        with allure.step("5.选择配送方式，确认配送"):
            checkout_page.select_shipping_method()

        with allure.step("6.选择支付方式，确认支付"):
            checkout_page.select_payment_method()

        with allure.step("7.勾选服务协议，提交订单"):
            checkout_page.agree_terms()
            checkout_page.confirm_order()
            checkout_page.verify_order_success()