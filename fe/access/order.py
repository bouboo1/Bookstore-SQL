import requests
from urllib.parse import urljoin


class Order:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "order/")

    def new_order_cancel(self, user_id: str, order_id: str):
        json = {
            "user_id": user_id,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "new_order_cancel")
        r = requests.post(url, json=json)
        return r.status_code

    def check_order(self, user_id: str):
        json = {
            "user_id": user_id
        }
        url = urljoin(self.url_prefix, "check_order")
        r = requests.post(url, json=json)
        return r.status_code

    def check_order_status(self):
        json = {}
        url = urljoin(self.url_prefix, "check_order_status")
        r = requests.post(url, json=json)
        return r.status_code