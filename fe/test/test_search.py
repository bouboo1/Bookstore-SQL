import json
import pytest
from fe.access import search
import pymysql
from fe import conf

conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='zwx870504',
            database='bookstore'
        )
cursor = conn.cursor()

cursor.execute(
            """
            INSERT INTO store (store_id, book_id, tags, pictures, id, title, author, publisher, original_title,
                                translator, pub_year, pages, price, binding, isbn, author_intro, book_intro, content,
                                stock_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            ('store1', '1000121', 'kunchong', json.dumps([]), '1000121', 'kunchongji', 'fabuer', 'zuojia', '',
             'wangguang', '2004-03', 352,
             1900, 'pingzhuang', '9787506312820', 'fabuer', 'kunchongji', 'mulu\n', 10)
        )

conn.commit()
cursor.close()
conn.close()

class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.search = search.Search(conf.URL)
        self.search_query = "kunchong"
        self.search_scopes = ["title", "tags", "content", "book_intro"]
        self.store_name = "store1"

    def test_search_books(self):
        status, result = self.search.books(self.search_query, self.search_scopes)
        assert status == 200

    def test_search_books_wrong(self):
        status, result = self.search.books('txh', self.search_scopes)
        assert status == 404

    def test_search_stores(self):
        status, result = self.search.stores(self.store_name, self.search_query, self.search_scopes)
        assert status == 200

    def test_search_stores_wrong(self):
        status, result = self.search.stores('store111', self.search_query, self.search_scopes)
        assert status == 404

    def test_search_books_no_scope(self):
        search_query = "kunchong"
        search_scopes = []
        status, result = self.search.books(search_query, search_scopes)
        assert status == 200

    def test_search_books_no_query_and_scope(self):
        search_query = ""
        search_scopes = []
        status, result = self.search.books(search_query, search_scopes)
        assert status == 200

    def test_search_books_single_scope_no_match(self):
        search_query = "txh"
        search_scopes = ["title"]
        status, result = self.search.books(search_query, search_scopes)
        assert status == 404

    def test_search_books_multiple_scopes_no_match(self):
        search_query = "txh"
        search_scopes = ["title", "tags", "content"]
        status, result = self.search.books(search_query, search_scopes)
        assert status == 404

    def test_search_stores_single_store_no_match(self):
        store_name = "store1"
        search_query = "txh"
        search_scopes = ["title"]
        status, result = self.search.stores(store_name, search_query, search_scopes)
        assert status == 404

    def test_search_stores_multiple_stores_no_match(self):
        store_name = "store1"
        search_query = "txh"
        search_scopes = ["title", "tags", "content"]
        status, result = self.search.stores(store_name, search_query, search_scopes)
        assert status == 404