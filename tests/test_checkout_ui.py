import allure
from playwright.sync_api import Page
from flows.checkout_flow import CheckoutFlow
from config import TEST_EMAIL, TEST_PASSWORD


@allure.epic("OpenCart前台电商系统")
@allure.feature("结算下单模块")
class TestCheckoutUI:

    @allure.story("正向完整结算流程")
    @allure.title("TC-UI-CHECKOUT-001：登录-搜索商品-加购-结算下单正向流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("测试步骤：用户登录→搜索MacBook商品→加入购物车→进入结算页→选择地址、配送、支付方式，完成订单提交")
    def test_checkout_success(self, page: Page):
        flow = CheckoutFlow(page)
        flow.full_checkout_process(TEST_EMAIL, TEST_PASSWORD, "MacBook")