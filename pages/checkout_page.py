import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class CheckoutPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        # 地址相关
        self.new_address_radio = (By.XPATH, "//label[contains(text(),'I want to use a new address')]/input")
        self.firstname_input = (By.NAME, "firstname")
        self.lastname_input = (By.NAME, "lastname")
        self.address1_input = (By.NAME, "address_1")
        self.city_input = (By.NAME, "city")
        self.postcode_input = (By.NAME, "postcode")
        self.country_select = (By.NAME, "country_id")
        self.zone_select = (By.NAME, "zone_id")
        self.save_address_btn = (By.CSS_SELECTOR, "#shipping-address button[contains(text(),'Continue')]")

        # 配送支付
        self.shipping_choose_btn = (By.XPATH, "(//button[normalize-space()='Choose'])[1]")
        self.payment_choose_btn = (By.XPATH, "(//button[normalize-space()='Choose'])[2]")
        self.shipping_flat_option = (By.XPATH, "//label[contains(text(),'Flat Shipping Rate')]/input")
        self.payment_cod_option = (By.XPATH, "//label[contains(text(),'Cash On Delivery')]/input")
        self.popup_continue_btn = (By.CSS_SELECTOR, "div[role='dialog'] button[normalize-space()='Continue']")

        # 确认订单
        self.agree_checkbox = (By.XPATH, "//label[contains(text(),'I have read and agree to the Terms & Conditions')]/input")
        self.confirm_order_btn = (By.XPATH, "//button[normalize-space()='Confirm Order']")
        self.order_success_title = (By.CSS_SELECTOR, "#content h1")

    def fill_address(self, firstname, lastname, address, city, postcode):
        """智能处理地址：如果页面已有 Confirm Order，跳过地址填写"""
        self.wait_network_idle(wait_sec=2)
        confirm_btn_list = self.driver.find_elements(*self.confirm_order_btn)
        if len(confirm_btn_list) > 0:
            logger.info("检测到Confirm Order按钮，跳过地址填写")
            return self

        # 选择已有地址
        shipping_radio = (By.CSS_SELECTOR, "input[type='radio'][name='shipping_address']")
        radio_list = self.driver.find_elements(*shipping_radio)
        if len(radio_list) > 0:
            logger.info("选择已有地址")
            radio_list[0].click()
            cont_btn = (By.XPATH, "//button[normalize-space()='Continue']")
            self.click(cont_btn)
            self.wait_network_idle(wait_sec=3)
            logger.info("已选择已有地址")
            return self

        # 新建地址
        logger.info("尝试新建地址")
        fn_list = self.driver.find_elements(*self.firstname_input)
        if len(fn_list) > 0:
            self.input_text(self.firstname_input, firstname)
            self.input_text(self.lastname_input, lastname)
            self.input_text(self.address1_input, address)
            self.input_text(self.city_input, city)
            self.input_text(self.postcode_input, postcode)

            # 下拉选择国家地区
            country_elems = self.driver.find_elements(*self.country_select)
            if len(country_elems) > 0:
                from selenium.webdriver.support.ui import Select
                Select(country_elems[0]).select_by_visible_text("United Kingdom")
            zone_elems = self.driver.find_elements(*self.zone_select)
            if len(zone_elems) > 0:
                Select(zone_elems[0]).select_by_visible_text("Greater London")

            save_btn_list = self.driver.find_elements(*self.save_address_btn)
            if len(save_btn_list) > 0:
                self.click(self.save_address_btn)
                self.wait_network_idle(wait_sec=2.5)
            logger.info("地址已填写")
        else:
            logger.warning("未找到地址字段，假设已存在")
        return self

    def select_shipping_method(self):
        """选择配送方式（如果有），否则跳过"""
        self.wait_network_idle(wait_sec=2)
        shipping_radio = (By.NAME, "shipping_method")
        radio_list = self.driver.find_elements(*shipping_radio)
        if len(radio_list) > 0:
            radio_list[0].click()
            cont_btn = (By.XPATH, "(//button[normalize-space()='Continue'])[last()]")
            self.click(cont_btn)
            self.wait_network_idle(wait_sec=2)
            logger.info("配送方式选择完成")
        else:
            logger.warning("未检测到配送方式，跳过")
        return self

    def select_payment_method(self):
        """智能选择支付方式：适用任何结算页面"""
        self.wait_network_idle(wait_sec=3)
        # 检查是否已经出现银行转账提示
        bank_text_loc = (By.XPATH, "//*[contains(text(),'Bank Transfer Instructions')]")
        bank_list = self.driver.find_elements(*bank_text_loc)
        if len(bank_list) > 0:
            logger.info("支付方式已确认，跳过")
            return self

        # 点击Choose按钮
        choose_btn_list = self.driver.find_elements(By.XPATH, "//button[normalize-space()='Choose']")
        if len(choose_btn_list) > 0:
            choose_btn_list[0].click()
            self.wait_network_idle(wait_sec=2)
            logger.info("点击 Choose 按钮")

        # 优先选Bank Transfer
        bank_transfer_loc = (By.XPATH, "//*[contains(text(),'Bank Transfer')]")
        bank_tf_list = self.driver.find_elements(*bank_transfer_loc)
        if len(bank_tf_list) > 0:
            bank_tf_list[0].click()
            self.wait_network_idle(wait_sec=1)
            logger.info("选择 Bank Transfer")
        else:
            radio_all = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if len(radio_all) > 0:
                radio_all[0].click()
                self.wait_network_idle(wait_sec=1)
                logger.info("选择第一个支付方式")
            else:
                label_list = self.driver.find_elements(By.CSS_SELECTOR, ".form-check-label,.radio label")
                if len(label_list) > 0:
                    label_list[0].click()
                    self.wait_network_idle(wait_sec=1)
                    logger.info("点击支付选项")
        # 点Continue
        cont_btn_all = self.driver.find_elements(By.XPATH, "//button[normalize-space()='Continue']")
        if len(cont_btn_all) > 0:
            self.scroll_to_bottom()
            cont_btn_all[-1].click()
            self.wait_network_idle(wait_sec=3)
            logger.info("点击 Continue 按钮")
        # 校验支付确认提示
        try:
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located(bank_text_loc))
            logger.info("支付方式已确认（出现 Instructions）")
        except Exception:
            logger.warning("未出现 Instructions，检查 Confirm Order 是否启用")
            confirm_btn_list = self.driver.find_elements(*self.confirm_order_btn)
            if len(confirm_btn_list) > 0:
                if confirm_btn_list[0].is_enabled():
                    logger.info("Confirm Order 已启用")
                else:
                    logger.warning("Confirm Order 可见但未启用，尝试再点一次 Continue")
                    if len(cont_btn_all) >0:
                        cont_btn_all[-1].click()
                        self.wait_network_idle(wait_sec=3)
        logger.info("支付方式选择完成")
        return self

    def confirm_order(self):
        logger.info("提交确认订单")
        self.scroll_to_bottom()
        self.wait_network_idle(wait_sec=1)
        confirm_btn_list = self.driver.find_elements(*self.confirm_order_btn)
        if len(confirm_btn_list) == 0:
            raise Exception("未找到 Confirm Order 按钮")
        try:
            WebDriverWait(self.driver,5).until(EC.element_to_be_clickable(self.confirm_order_btn))
            confirm_btn_list[0].click()
            logger.info("Confirm Order 正常点击")
        except Exception:
            logger.warning("Confirm Order 未启用，JS兜底点击")
            self.driver.execute_script("arguments[0].click();", confirm_btn_list[0])
        self.wait_network_idle(wait_sec=3)
        if "success" in self.driver.current_url:
            logger.info("已跳转到成功页面")
        else:
            logger.warning(f"当前URL: {self.driver.current_url}")
        logger.info("订单提交完成")
        return self

    def verify_order_success(self):
        current_url = self.driver.current_url
        if "checkout/success" in current_url or "route=checkout/success" in current_url:
            logger.info("已跳转到成功页面")
            return
        elem = self.find_element(self.order_success_title)
        title = elem.text.strip()
        success_keywords = ["Your order has been placed", "Order Placed", "Success"]
        assert any(kw in title for kw in success_keywords), f"订单未提交成功，当前标题: {title}"
        logger.info("订单提交成功，用例执行通过")

    def skip_terms_and_scroll(self):
        """OpenCart 4 结算页无服务协议，仅滚动到页面底部"""
        logger.info("跳过协议勾选（结算页无服务协议），仅滚动到页面底部")
        self.scroll_to_bottom()
        self.wait_network_idle(wait_sec=1)
        return self