from be.model import error
from datetime import datetime, timedelta
from be.model import db_conn


class Order(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # 订单取消 增加余额 增加库存
    def new_order_cancel(self, user_id: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            # 未支付订单取消：手动取消\自动取消
            # 手动取消
            cursor.execute(
                "SELECT order_id, store_id, user_id, book_status, order_time FROM new_order WHERE order_id = %s",
                (order_id,),
            )
            new_order_result = cursor.fetchone()

            if new_order_result is not None:
                order_id, store_id, buyer_id, book_status, order_time = new_order_result
                if buyer_id != user_id:
                    return error.error_authorization_fail()

                cursor.execute("DELETE FROM new_order WHERE order_id = %s", (order_id,))

            # 如果已经支付的话需要取消订单以后减少商家余额，增加用户余额
            else:
                cursor.execute(
                    "SELECT order_id, store_id, user_id, book_status, price FROM new_order_paid WHERE order_id = %s",
                    (order_id,)
                )
                new_order_paid_result = cursor.fetchone()
                if new_order_paid_result:
                    order_id, store_id, buyer_id, book_status, price = new_order_paid_result
                    if buyer_id != user_id:
                        return error.error_authorization_fail()

                    # 减少卖家余额
                    cursor.execute(
                        "UPDATE user SET balance = balance - %s WHERE user_id = %s",
                        (price, store_id)
                    )

                    # 增加买家余额
                    cursor.execute(
                        "UPDATE user SET balance = balance + %s WHERE user_id = %s",
                        (price, buyer_id)
                    )

                    # 删除订单
                    cursor.execute("DELETE FROM new_order_paid WHERE order_id = %s", (order_id,))

                else:
                    return error.error_invalid_order_id(order_id)

                # 增加书籍库存
                cursor.execute(
                    "SELECT book_id, count FROM new_order_detail WHERE order_id = %s",
                    (order_id,)
                )
                orders_result = cursor.fetchall()
                for order_result in orders_result:
                    book_id, count = order_result
                    cursor.execute(
                        "UPDATE store SET stock_level = stock_level + %s WHERE store_id = %s AND book_id = %s",
                        (count, store_id, book_id)
                    )
                self.conn.commit()
            return 200, "ok"
        finally:
            cursor.close()

    # 查询历史订单
    def check_order(self, user_id: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            # 查询未付款订单
            cursor.execute(
                "SELECT order_id, store_id, user_id, book_status, order_time FROM new_order WHERE user_id = %s",
                (user_id,),
            )
            new_orders_result = cursor.fetchall()
            if new_orders_result:
                for new_order_result in new_orders_result:
                    order_id = new_order_result[0]
                    cursor.execute(
                        "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s",
                        (order_id,)
                    )

                    new_order_details_result = cursor.fetchall()
                    if new_order_details_result:
                        return error.error_invalid_order_id(order_id)

            # 查询已付款订单
            cursor.execute(
                "SELECT order_id, store_id, user_id, book_status, price FROM new_order_paid WHERE user_id = %s",
                (user_id,)
            )

            new_orders_paid_result = cursor.fetchall()
            if new_orders_paid_result:
                for new_order_paid_results in new_orders_paid_result:
                    order_id = new_order_paid_results[0]
                    cursor.execute(
                        "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s",
                        (order_id,)
                    )
                    new_order_details_result = cursor.fetchall()
                    # if new_order_details_result:
                    #     return error.error_invalid_order_id(order_id)
            if not new_orders_paid_result:
                return error.error_invalid_order_id(order_id)
            return 200, "ok"
        except Exception as e:
            print(e)
            return 500, "Internal Server Error"
        finally:
            cursor.close()

    def check_order_status(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            timeout_datetime = datetime.now() - timedelta(seconds=5)

            # Assuming the new_orders table has an 'order_time' column
            cursor.execute("DELETE FROM new_order WHERE order_time <= %s", (timeout_datetime,))
            return 200, "ok"
        finally:
            cursor.close()