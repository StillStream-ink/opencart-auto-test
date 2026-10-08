import allure
from pages.cart_page import CartPage
from pages.product_page import ProductPage


class TestCartUI:
    @allure.feature("购物车模块")
    @allure.story("修改商品数量")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("更新购物车商品数量为9，校验商品数量")
    def test_cart_update_quantity(self, cart_clean):
        product_page = ProductPage(cart_clean)
        product_page.open_product(40)
        product_page.add_to_cart(1)
        cart_page = CartPage(cart_clean)
        cart_page.open_cart()
        cart_page.update_quantity(9)
        item_list = cart_page.get_cart_items_info()
        assert len(item_list) == 1
        assert item_list[0]["quantity"] == "9"

    @allure.feature("购物车模块")
    @allure.story("删除商品")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("删除购物车商品，校验购物车为空")
    def test_cart_remove_item(self, cart_clean):
        product_page = ProductPage(cart_clean)
        product_page.open_product(40)
        product_page.add_to_cart(1)
        cart_page = CartPage(cart_clean)
        cart_page.open_cart()
        items = cart_page.remove_item()
        assert len(items) == 0

    @allure.feature("购物车模块")
    @allure.story("数量边界校验")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("购物车输入数量0，提交后商品自动移除")
    def test_cart_input_zero(self, cart_clean):
        product_page = ProductPage(cart_clean)
        product_page.open_product(40)
        product_page.add_to_cart(1)
        cart_page = CartPage(cart_clean)
        cart_page.open_cart()
        cart_page.update_quantity(0)
        item_list = cart_page.get_cart_items_info()
        # OpenCart特性：数量0提交，商品直接移除购物车
        assert len(item_list) == 0

    @allure.feature("购物车模块")
    @allure.story("购物车修改商品数量")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("购物车页面修改商品数量，数量更新为2")
    def test_cart_add_same_product(self, cart_clean):
        product_page = ProductPage(cart_clean)
        product_page.open_product(40)
        product_page.add_to_cart(1)
        cart_page = CartPage(cart_clean)
        cart_page.open_cart()
        cart_page.update_quantity(2)
        item_list = cart_page.get_cart_items_info()
        assert len(item_list) == 1
        assert item_list[0]["quantity"] == "2"