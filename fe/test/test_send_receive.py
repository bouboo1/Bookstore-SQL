import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import time
from fe.access.send_receive import SendAndReceive
from fe import conf
import uuid


class TestSendAndReceive:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_send_receive_seller{}".format(str(uuid.uuid1()))
        self.store_id = "test_send_receive_store{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_send_receive_buyer{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        gen_book = GenBook(self.seller_id, self.store_id)

        self.seller = gen_book.seller
        ok, self.buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)

        self.buyer = b
        self.total_price = 0

        self.seller_book = SendAndReceive(conf.URL)

        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num

        code = self.buyer.add_funds(self.total_price + 10000000)
        assert code == 200

        code, self.order_id = b.new_order(self.store_id, self.buy_book_id_list)
        assert code == 200
        yield

    # 发货的测试here
    # 发货正常情况
    def test_ok_send(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller_book.send_books(self.seller_id, self.order_id)
        assert code == 200

    # 订单号 order_id 不存在
    def test_invalid_order_id_send(self):
        code = self.seller_book.send_books(self.seller_id, self.order_id + 'x')
        assert code != 200

    # 权限错误 user_id 与 store的user_id 不对应
    def test_authorization_error_send(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller_book.send_books(self.seller_id + 'x', self.order_id)
        assert code != 200

    # 订单已发货不可重复发货
    def test_books_duplicate_send_send(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller_book.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.seller_book.send_books(self.seller_id, self.order_id)
        assert code != 200

    # 订单未付款
    def test_order_not_paid_send(self):
        code = self.seller_book.send_books(self.seller_id, self.order_id)
        assert code != 200


    # 收货的测试here
    # 收货正常
    def test_ok_receive(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller_book.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.seller_book.receive_books(self.buyer_id, self.order_id)
        assert code == 200

    # 权限错误 buyer_id 与 user_id 不对应
    def test_authorization_error_receive(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller_book.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.seller_book.receive_books(self.buyer_id + 'x', self.order_id)
        assert code != 200

    # 订单号 order_id 不存在
    def test_invalid_order_id_receive(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller_book.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.seller_book.receive_books(self.buyer_id, self.order_id + 'x')
        assert code != 200

    # 订单未发货
    def test_books_not_send_receive(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller_book.receive_books(self.buyer_id, self.order_id)
        assert code != 200

    # 订单未付款
    # def test_books_not_paid_receive(self):
    #     code = self.seller_book.receive_books(self.buyer_id, self.order_id)
    #     assert code != 200

    def test_books_already_received(self):
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller_book.send_books(self.seller_id, self.order_id)
        assert code == 200
        code = self.seller_book.receive_books(self.buyer_id, self.order_id)
        assert code == 200
        code = self.seller_book.receive_books(self.buyer_id, self.order_id)
        assert code != 200


    # def test_books_not_paid(self):
    #     code = self.seller_book.receive_books('user1', 'order1')
    #     assert code == 520