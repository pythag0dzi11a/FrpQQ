import os.path
import sqlite3

from frp_detector import FrpStatus


class DataBaseManager:
    def __init__(self):
        self.__database_name = "data.db"
        if not os.path.exists(self.__database_name):
            print("Database not found. Create new database. Please check if something goes wrong.")
            self.init_database()
        self.__connection = sqlite3.connect(self.__database_name)
        self.__cursor = self.__connection.cursor()

    def init_database(self):
        self.__cursor.execute('''CREATE TABLE IF NOT EXISTS frp_status
                                 (
                                     id           INTEGER PRIMARY KEY,
                                     proxy_name   TEXT,
                                     proxy_type   TEXT,
                                     proxy_status TEXT,
                                     last_start   TEXT,
                                     last_close   TEXT,
                                     proxy_port   TEXT
                                 );''')
        self.__connection.commit()
        self.__connection.close()

    def insert_new_record(self, data: FrpStatus):
        pass
