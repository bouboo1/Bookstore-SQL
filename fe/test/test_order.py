import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
from fe.access.order import Order
from fe import conf
import time
import uuid


class TestOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_order_seller{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_store{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_order_buyer{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        gen_book = GenBook(self.seller_id, self.store_id)

        self.wait_time = 10  # 10s后自动取消订单
        self.seller = gen_book.seller
        ok, self.buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.buyer_id)

        self.buyer = b
        self.total_price = 0

        self.buyer_order = Order(conf.URL)

        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num

        code = self.buyer.add_funds(self.total_price + 10000)
        assert code == 200

        code, self.order_id = b.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        yield

    # 已付款订单的取消
    def test_ok_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
        assert code == 200

    # 未付款订单的取消
    def test_ok_not_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
        assert code == 200

    # 已付款订单号 order_id 不存在
    def test_invalid_order_id_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id + 'x')
        assert code != 200

    # 未付款订单号 order_id 不存在
    def test_invalid_order_id_not_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id + 'x')
        assert code != 200

    # 取消已付款订单时buyer_id与user_id不匹配
    def test_authorization_error_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id + 'x', self.order_id)
        assert code != 200

    # 取消未付款订单时buyer_id与user_id不匹配
    def test_authorization_error_not_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id + 'x', self.order_id)
        assert code != 200

    # 已付款订单不可重复取消
    def test_duplicate_cancel_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
        assert code != 200

    # 未付款订单不可重复取消
    def test_duplicate_cancel_not_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
        assert code != 200

    # 查询已付款订单
    def test_ok_check_have_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.check_order(self.buyer_id)
        assert code == 200

    # 查询未付款订单
    def test_ok_check_not_paid(self):
        code = self.buyer_order.check_order(self.buyer_id)
        assert code != 200

    # 未付款用户不匹配
    def test_invalid_order(self):
        code = self.buyer_order.check_order(self.buyer_id + 'x')
        assert code != 200

    # 已付款用户不匹配
    def test_invalid_order_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.check_order(self.buyer_id + 'x')
        assert code != 200

    # 未付款订单号 order_id 不存在
    def test_invalid_order_id_check_not_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id + 'x')
        assert code != 200


    def test_invalid_order_id_check_paid(self):
        # code, self.order_id = self.buyer.new_order(self.store_id, self.buy_book_id_list)
        # assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id + 'x')
        assert code != 200

    # def test_ok_overtime(self):
    #     time.sleep(self.wait_time + 10)
    #     code = self.buyer_order.check_order_status()
    #     assert code != 200

    def test_timeout(self):
        time.sleep(self.wait_time)
        self.buyer_order.check_order_status()
        code = self.buyer_order.new_order_cancel(self.buyer_id, self.order_id)
        assert code != 200