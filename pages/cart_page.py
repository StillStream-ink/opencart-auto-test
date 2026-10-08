from pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import allure


class CartPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.cart_rows = (By.CSS_SELECTOR, ".table-responsive tbody tr")

    @allure.step("打开购物车页面")
    def open_cart(self):
        self.goto("http://127.0.0.1/opencart/index.php?route=checkout/cart")
        # 跳转后给页面渲染时间
        time.sleep(1)

    @allure.step("更新购物车第一件商品数量：{qty}")
    def update_quantity(self, qty: int):
        # 等待【可见】的购物车行，而不只是DOM存在
        self.wait.until(EC.visibility_of_any_elements_located(self.cart_rows))
        rows = self.driver.find_elements(*self.cart_rows)
        assert len(rows) > 0, "购物车无商品，无法修改数量"
        first_row = rows[0]

        qty_input = first_row.find_element(By.CSS_SELECTOR, "input[name='quantity']")
        btn_update = first_row.find_element(By.CSS_SELECTOR, "button[formaction*='cart.edit']")

        qty_input.clear()
        qty_input.send_keys(str(qty))
        btn_update.click()
        time.sleep(2)
        self.driver.refresh()
        time.sleep(1)
        return self.get_cart_items_info()

    @allure.step("删除购物车内第一件商品")
    def remove_item(self):
        self.wait.until(EC.visibility_of_any_elements_located(self.cart_rows))
        rows = self.driver.find_elements(*self.cart_rows)
        if len(rows) == 0:
            return []
        first_row = rows[0]
        btn_remove = first_row.find_element(By.CSS_SELECTOR, "a[href*='cart.remove']")
        btn_remove.click()
        time.sleep(2)
        self.driver.refresh()
        return self.get_cart_items_info()

    @allure.step("获取购物车商品列表信息")
    def get_cart_items_info(self):
        item_list = []
        rows = self.driver.find_elements(*self.cart_rows)
        for row in rows:
            try:
                qty_input = row.find_element(By.CSS_SELECTOR, "input[name='quantity']")
                qty = qty_input.get_attribute("value")
                item_list.append({"quantity": qty})
            except Exception:
                continue
        return item_list