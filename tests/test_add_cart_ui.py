import allure
import pytest
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from config import TEST_EMAIL, TEST_PASSWORD


@allure.feature("购物车模块")
@allure.story("商品加入购物车")
class TestAddCartUI:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        self.login_page = LoginPage(driver)
        self.product_page = ProductPage(driver)
        self.cart_page = CartPage(driver)
        self.login_page.navigate()
        self.login_page.login(TEST_EMAIL, TEST_PASSWORD)

    @allure.title("正常添加商品到购物车，校验购物车内存在商品")
    def test_add_product_to_cart(self):
        self.product_page.open_product(40)
        self.product_page.add_to_cart()
        # 不去捕获一闪而过的提示弹窗，直接打开购物车校验商品
        self.cart_page.open_cart()
        item_list = self.cart_page.get_cart_items_info()
        assert len(item_list) >= 1, "加入购物车失败，购物车为空"