import logging
import os
# import sqlite3 as sqlite
import pymysql


class Store:
    database: str

    def __init__(self):

        self.database = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='zwx870504',
            database='bookstore'
        )
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS user ("
                "user_id VARCHAR(255) PRIMARY KEY, password VARCHAR(255) NOT NULL, "
                "balance INTEGER NOT NULL, token TEXT, terminal VARCHAR(255));"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS user_store("
                "user_id VARCHAR(255), store_id VARCHAR(255), PRIMARY KEY(user_id, store_id));"
            )

            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS store( "
            #     "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
            #     " PRIMARY KEY(store_id, book_id))"
            # )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS store(
                    store_id VARCHAR(255),
                    book_id VARCHAR(255),
                    tags VARCHAR(255),
                    book_info LONGTEXT,
                    pictures BLOB,
                    id VARCHAR(255),
                    title VARCHAR(255),
                    author VARCHAR(255),
                    publisher VARCHAR(255),
                    original_title VARCHAR(255),
                    translator VARCHAR(255),
                    pub_year VARCHAR(255),
                    pages INTEGER,
                    price INTEGER,
                    binding VARCHAR(255),
                    isbn VARCHAR(255),
                    author_intro VARCHAR(255),
                    book_intro VARCHAR(255),
                    content TEXT,
                    stock_level INTEGER,
                    PRIMARY KEY (store_id, book_id)
                    )
                """
            )

            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            # )
            #
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id))"
            # )
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS new_order ("
                "order_id VARCHAR(255) PRIMARY KEY, "
                "store_id VARCHAR(255), "
                "user_id VARCHAR(255), "
                "book_status INTEGER, "
                "order_time DATETIME)"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS new_order_detail( "
                "order_id VARCHAR(255), book_id VARCHAR(255), count INTEGER, price INTEGER,  "
                "PRIMARY KEY(order_id, book_id))"
            )

            cursor.execute(
                "CREATE TABLE IF NOT EXISTS new_order_paid( "
                "order_id VARCHAR(255), store_id VARCHAR(255), user_id VARCHAR(255), "
                "book_status INTEGER, price INTEGER, "
                "PRIMARY KEY(order_id, user_id))"
            )

            conn.commit()
        finally:
            if cursor:
                cursor.close()


    def get_db_conn(self) -> pymysql.connections.Connection:
        return self.database


database_instance = Store()


def init_database():
    global database_instance
    database_instance = Store()


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
