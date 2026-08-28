from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # 地址相关（如果存在）
        self.new_address_radio = self.page.get_by_label("I want to use a new address")
        self.firstname_input = self.page.locator("input[name='firstname']")
        self.lastname_input = self.page.locator("input[name='lastname']")
        self.address1_input = self.page.locator("input[name='address_1']")
        self.city_input = self.page.locator("input[name='city']")
        self.postcode_input = self.page.locator("input[name='postcode']")
        self.country_select = self.page.locator("select[name='country_id']")
        self.zone_select = self.page.locator("select[name='zone_id']")
        self.save_address_btn = self.page.locator("#shipping-address").get_by_role("button", name="Continue")

        # 配送/支付弹窗（如果存在）
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
        """智能处理地址：如果页面已有 Confirm Order，跳过地址填写"""
        self.page.wait_for_timeout(2000)

        if self.page.locator("button:has-text('Confirm Order')").is_visible(timeout=2000):
            print("🔹 检测到Confirm Order按钮，跳过地址填写")
            return self

        # 尝试选择已有地址
        if self.page.locator("input[type='radio'][name='shipping_address']").is_visible(timeout=3000):
            print("🔹 选择已有地址")
            self.page.locator("input[type='radio'][name='shipping_address']").first.click()
            self.page.wait_for_timeout(500)
            self.page.click("button:has-text('Continue')")
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(3000)
            print("✅ 已选择已有地址")
            return self

        # 尝试新建地址（如果存在相关字段）
        print("🔹 尝试新建地址")
        if self.firstname_input.count() > 0:
            self.firstname_input.fill(firstname)
            self.lastname_input.fill(lastname)
            self.address1_input.fill(address)
            self.city_input.fill(city)
            self.postcode_input.fill(postcode)
            if self.country_select.count() > 0:
                self.country_select.select_option(label="United Kingdom")
            if self.zone_select.count() > 0:
                self.zone_select.select_option(label="Greater London")
            if self.save_address_btn.count() > 0:
                self.save_address_btn.click()
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_timeout(2500)
            print("✅ 地址已填写")
        else:
            print("⚠️ 未找到地址字段，假设已存在")

        return self

    def select_shipping_method(self):
        """选择配送方式（如果有），否则跳过"""
        self.page.wait_for_timeout(2000)
        shipping_input = self.page.locator("input[name='shipping_method']")
        if shipping_input.count() > 0:
            shipping_input.first.check()
            self.page.wait_for_timeout(500)
            continue_btn = self.page.locator("button:has-text('Continue')").last
            continue_btn.click()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_timeout(2000)
            print("✅ 配送方式选择完成")
        else:
            print("⚠️ 未检测到配送方式，跳过")
        return self

    def select_payment_method(self):
        """智能选择支付方式：适用任何结算页面"""
        self.page.wait_for_timeout(3000)

        # 1. 检查是否已经存在 "Bank Transfer Instructions"（支付已确认）
        if self.page.locator("text=Bank Transfer Instructions").is_visible(timeout=2000):
            print("✅ 支付方式已确认，跳过")
            return self

        # 2. 尝试点击 "Choose" 按钮（如果有）
        choose_btn = self.page.locator("button:has-text('Choose')")
        if choose_btn.count() > 0 and choose_btn.first.is_visible():
            choose_btn.first.click()
            self.page.wait_for_timeout(2000)
            print("✅ 点击 Choose 按钮")

        # 3. 尝试选择支付方式（优先 Bank Transfer）
        bank_transfer = self.page.locator("text=Bank Transfer")
        if bank_transfer.count() > 0:
            bank_transfer.first.click()
            self.page.wait_for_timeout(1000)
            print("✅ 选择 Bank Transfer")
        else:
            # 选择第一个可见的支付方式（单选按钮或标签）
            radio = self.page.locator("input[type='radio']")
            if radio.count() > 0:
                radio.first.check()
                self.page.wait_for_timeout(1000)
                print("✅ 选择第一个支付方式")
            else:
                # 尝试点击任何可见的支付选项文本
                payment_option = self.page.locator(".form-check-label, .radio label").first
                if payment_option.count() > 0:
                    payment_option.click()
                    self.page.wait_for_timeout(1000)
                    print("✅ 点击支付选项")

        # 4. 点击 "Continue" 按钮（如果有）
        continue_btn = self.page.locator("button:has-text('Continue')")
        if continue_btn.count() > 0:
            # 选择最后一个 Continue（通常是支付方式的确认按钮）
            continue_btn.last.scroll_into_view_if_needed()
            continue_btn.last.click(force=True)
            self.page.wait_for_timeout(3000)
            print("✅ 点击 Continue 按钮")

        # 5. 等待支付确认（"Bank Transfer Instructions" 出现或 Confirm Order 启用）
        try:
            self.page.wait_for_selector("text=Bank Transfer Instructions", timeout=5000)
            print("✅ 支付方式已确认（出现 Instructions）")
        except:
            print("⚠️ 未出现 Instructions，检查 Confirm Order 是否启用")
            confirm_btn = self.page.locator("button:has-text('Confirm Order')")
            if confirm_btn.count() > 0:
                confirm_btn.first.wait_for(state="visible", timeout=5000)
                if confirm_btn.first.is_enabled():
                    print("✅ Confirm Order 已启用")
                else:
                    print("⚠️ Confirm Order 可见但未启用，尝试再点一次 Continue")
                    if continue_btn.count() > 0:
                        continue_btn.last.click(force=True)
                        self.page.wait_for_timeout(3000)

        print("✅ 支付方式选择完成")
        return self

    def confirm_order(self):
        print("提交确认订单")
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)

        confirm_btn = self.page.locator("button:has-text('Confirm Order')")
        if confirm_btn.count() == 0:
            raise Exception("未找到 Confirm Order 按钮")

        # 尝试等待启用，如果超时就强制点击
        try:
            confirm_btn.first.wait_for(state="enabled", timeout=5000)
            confirm_btn.first.click()
            print("✅ Confirm Order 正常点击")
        except:
            print("⚠️ Confirm Order 未启用，强制点击")
            confirm_btn.first.click(force=True)

        self.page.wait_for_timeout(3000)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

        if "success" in self.page.url:
            print("✅ 已跳转到成功页面")
        else:
            print(f"⚠️ 当前URL: {self.page.url}")

        print("✅ 订单提交完成")
        return self

    def verify_order_success(self):
        current_url = self.page.url
        if "checkout/success" in current_url or "route=checkout/success" in current_url:
            print("✅ 已跳转到成功页面")
            return

        self.page.wait_for_selector("#content h1", timeout=5000)
        title = self.page.locator("#content h1").text_content() or ""
        success_keywords = ["Your order has been placed", "Order Placed", "Success"]
        assert any(kw in title for kw in success_keywords), f"订单未提交成功，当前标题: {title}"
        print("✅ 订单提交成功，用例执行通过")

    def agree_terms(self):
        print("⏭️ 跳过协议勾选（结算页无服务协议）")
        self._scroll_to_bottom()
        self.page.wait_for_timeout(1000)
        return self

    def _scroll_to_bottom(self):
        self.page.mouse.wheel(0, 5000)
        self.page.wait_for_timeout(300)
        self.page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
        self.page.wait_for_timeout(300)