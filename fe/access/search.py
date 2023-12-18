import requests
from urllib.parse import urljoin

class Search:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "search/")

    def books(self, search_query, search_scopes):
        json = {"search_query": search_query, "search_scopes": search_scopes}
        url = urljoin(self.url_prefix, "search_books")
        r = requests.post(url, json=json)
        if r.status_code == 200:
            return r.status_code, r.json()  # Return the status code and JSON response
        else:
            return r.status_code, None

    def stores(self, store_name, search_query, search_scopes):
        json = {"store_name": store_name, "search_query": search_query, "search_scopes": search_scopes}
        url = urljoin(self.url_prefix, "search_stores")
        r = requests.post(url, json=json)
        if r.status_code == 200:
            return r.status_code, r.json()  # Return the status code and JSON response
        else:
            return r.status_code, None