from be.model import error
from be.model import db_conn

class SendAndReceive(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def send_books(self, user_id: str, order_id: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM new_order_paid WHERE order_id = %s", (order_id,))
            result = cursor.fetchone()

            if result is None:
                cursor.execute("SELECT * FROM new_order WHERE order_id = %s", (order_id,))
                result_not_paid = cursor.fetchone()
                if result_not_paid is not None:
                    books_status = result_not_paid[3]
                    if books_status == 2:
                        return error.error_not_paid_book()
                else:
                    return error.error_invalid_order_id(order_id)

            store_id = result[1]  # 换成使用索引查找
            books_status = result[3]

            # 根据store_id找卖家
            cursor.execute("SELECT * FROM user_store WHERE store_id = %s", (store_id,))
            seller_result = cursor.fetchone()
            seller_id = seller_result[0]

            if seller_id != user_id:
                return error.error_authorization_fail()

            if books_status == 0:
                return error.error_book_has_sent()


            # Update the books_status in the MySQL database
            cursor.execute("UPDATE `new_order_paid` SET book_status = 0 WHERE order_id = %s", (order_id,))
            self.conn.commit()

            return 200, "ok"

        finally:
            if cursor:
                cursor.close()

    def receive_books(self, user_id: str, order_id: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM new_order_paid WHERE order_id = %s", (order_id,))
            result = cursor.fetchone()

            if result is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = result[2]
            books_status = result[3]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            if books_status == 1:
                return error.error_book_has_not_sent()

            if books_status == 3:
                return error.error_book_has_received()

            # Update the books_status in the MySQL database
            cursor.execute("UPDATE `new_order_paid` SET book_status = 3 WHERE order_id = %s", (order_id,))
            self.conn.commit()

            return 200, "ok"

        finally:
            if cursor:
                cursor.close()