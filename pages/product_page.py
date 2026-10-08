from pages.base_page import BasePage
from selenium.webdriver.common.by import By
import allure

class ProductPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.btn_add_to_cart = (By.ID, "button-cart")

    @allure.step("打开商品详情页，商品id:{product_id}")
    def open_product(self, product_id: int):
        url = f"http://127.0.0.1/opencart/index.php?route=product/product&product_id={product_id}"
        self.goto(url)

    @allure.step("添加商品到购物车，数量：{num}")
    def add_to_cart(self, num: int = 1):
        # 数量输入框
        input_qty = (By.ID, "input-quantity")
        self.input_text(input_qty, str(num))
        self.click(self.btn_add_to_cart)