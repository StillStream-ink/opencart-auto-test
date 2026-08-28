from pages.login_page import LoginPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from playwright.sync_api import Page
from config import BASE_URL
import allure


class CheckoutFlow:
    def __init__(self, page: Page):
        self.page = page
        self.login_page = LoginPage(page)
        self.cart_page = CartPage(page)
        self.checkout_page = CheckoutPage(page)

    def full_checkout_process(self, email, password, product_name):
            # 清除历史cookie，避免上次登录状态残留
        self.page.context.clear_cookies()
        self.page.wait_for_timeout(500)

        # 1.优先登录会员账号
        with allure.step("1.访问登录页面，执行账号登录"):
            self.login_page.navigate()
            self.login_page.login(email, password)
            self.login_page.verify_login_success()
            self.page.wait_for_timeout(2000)

        # ============【新增：登录后清空历史购物车商品】============
        with allure.step("1.1 清空购物车历史遗留商品"):
            self.cart_page.clear_cart()

        # 2.登录完成后，搜索并添加商品（存入会员购物车）
        with allure.step(f"2.搜索商品：{product_name}，添加至购物车"):
            self.cart_page.navigate()
            self.cart_page.search_and_add_product(product_name)
            self.page.wait_for_timeout(3000)  # 延长等待，给OC写入会话时间

        # 3.进入购物车页面，跳转结算页
        with allure.step("3.进入购物车，跳转结算页面"):
            self.cart_page.go_to_checkout()

        # 4.结算页面填写收货地址
        self.checkout_page.fill_address(
            firstname="John",
            lastname="Doe",
            address="123 Main Street",
            city="London",
            postcode="SW1A 1AA"
        )
        # 5.选择配送方式
        with allure.step("5.选择配送方式"):
            self.checkout_page.select_shipping_method()

        # 6.选择支付方式
        with allure.step("6.选择支付方式"):
            self.checkout_page.select_payment_method()

        # 7.同意协议并提交订单
        with allure.step("7.勾选服务协议，确认下单"):
            # self.checkout_page.agree_terms()
            self.checkout_page.confirm_order()

        # 8.校验下单成功页面
        with allure.step("8.验证订单提交成功"):
            self.checkout_page.verify_order_success()