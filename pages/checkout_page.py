from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # 地址相关
        self.new_address_radio = self.page.get_by_label("I want to use a new address")
        self.firstname_input = self.page.locator("input[name='firstname']")
        self.lastname_input = self.page.locator("input[name='lastname']")
        self.address1_input = self.page.locator("input[name='address_1']")
        self.city_input = self.page.locator("input[name='city']")
        self.postcode_input = self.page.locator("input[name='postcode']")
        self.country_select = self.page.locator("select[name='country_id']")
        self.zone_select = self.page.locator("select[name='zone_id']")
        self.save_address_btn = self.page.locator("#shipping-address").get_by_role("button", name="Continue")

        # 配送/支付弹窗
        self.shipping_choose_btn = self.page.get_by_role("button", name="Choose").first
        self.payment_choose_btn = self.page.get_by_role("button", name="Choose").nth(1)
        self.shipping_flat_option = self.page.get_by_label("Flat Shipping Rate - $14.00")
        self.payment_cod_option = self.page.get_by_label("Cash On Delivery")
        self.popup_continue_btn = self.page.get_by_role("dialog").get_by_role("button", name="Continue")

        # 确认订单
        self.agree_checkbox = self.page.get_by_label("I have read and agree to the Terms & Conditions")
        self.confirm_order_btn = self.page.get_by_role("button", name="Confirm Order")

        # 成功页
        self.order_success_title = self.page.locator("#content h1")

    def fill_address(self, firstname, lastname, address, city, postcode):
        """智能处理地址：优先选择已有地址，否则新建"""
        self.page.wait_for_timeout(3000)

        # 场景1：检测到已有地址列表
        if self.page.locator("input[type='radio'][name='shipping_address']").is_visible(timeout=3000):
            print("🔹 检测到已有地址列表，选择第一个地址")
            self.page.locator("input[type='radio'][name='shipping_address']").first.click()
            self.page.wait_for_timeout(500)
            self.page.click("button:has-text('Continue')")
            self.page.wait_for_timeout(3000)
            print("✅ 已选择已有地址")
            return self

        # 场景2：无地址，执行新建地址流程
        print("🔹 未检测到已有地址，进入新建地址流程")
        self.page.wait_for_selector("#shipping-address", timeout=15000)
        self.new_address_radio.wait_for(state="visible", timeout=10000)
        self.new_address_radio.check()
        self.page.wait_for_timeout(1000)

        self.firstname_input.fill(firstname)
        self.lastname_input.fill(lastname)
        self.address1_input.fill(address)
        self.city_input.fill(city)
        self.postcode_input.fill(postcode)

        self.country_select.select_option(label="United Kingdom")
        self.page.wait_for_timeout(1500)
        self.zone_select.select_option(label="Greater London")

        self.save_address_btn.scroll_into_view_if_needed()
        self.save_address_btn.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2500)
        print("✅ 地址已填写并提交")
        return self

    def select_shipping_method(self):
        self.page.wait_for_timeout(3000)
        self.shipping_choose_btn.scroll_into_view_if_needed()
        self.shipping_choose_btn.wait_for(state="visible", timeout=12000)
        self.shipping_choose_btn.click()
        self.shipping_flat_option.wait_for(state="visible", timeout=10000)
        self.shipping_flat_option.check()
        self.popup_continue_btn.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1500)
        print("✅ 配送方式选择完成")
        return self

    def select_payment_method(self):
        self.page.wait_for_timeout(3000)
        self.payment_choose_btn.scroll_into_view_if_needed()
        self.payment_choose_btn.wait_for(state="visible", timeout=12000)
        self.payment_choose_btn.click()
        self.payment_cod_option.wait_for(state="visible", timeout=10000)
        self.payment_cod_option.check()
        self.popup_continue_btn.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)
        print("✅ 支付方式选择完成")
        return self

    def agree_terms(self):
        print("⏭️ 跳过协议勾选（结算页无服务协议）")
        self._scroll_to_bottom()
        self.page.wait_for_timeout(1000)
        return self

    def confirm_order(self):
        print("提交确认订单")
        self._scroll_to_bottom()
        self.confirm_order_btn.scroll_into_view_if_needed()
        self.confirm_order_btn.wait_for(state="visible", timeout=10000)
        # 确保按钮启用（可选，但移除了无效的 wait_for state="enabled"）
        if not self.confirm_order_btn.is_enabled():
            print("⚠️ Confirm Order 按钮尚未启用，等待额外时间")
            self.page.wait_for_timeout(2000)
        self.confirm_order_btn.click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1500)
        print("✅ 订单提交完成")
        return self

    def verify_order_success(self):
        expect(self.order_success_title).to_contain_text("Your order has been placed!")
        print("✅ 订单提交成功，用例执行通过")

    def _scroll_to_bottom(self):
        self.page.mouse.wheel(0, 5000)
        self.page.wait_for_timeout(300)
        self.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        self.page.wait_for_timeout(300)