import sqlite3, threading
from Utils import General_Utils as utility




class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.lock = threading.Lock()
        self.config = utility.load_json("db_config")
        self.setup_database()

    def __del__(self):
        self.close()

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None


    def setup_database(self):
        with self.lock:
            for script in self.config["create"].values():
                self.cursor.execute(script)
            self.connection.commit()

    #
    # Life Queries
    #

    def get_life_total(self, user_id:int) -> int:
        with self.lock:
            self.cursor.execute(self.config['select']['select_life_totals_by_user_id'], (user_id,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                self.cursor.execute(self.config['insert']['insert_life_totals_by_user_id_and_total'], (user_id, 5))
                self.connection.commit()
                return 5

    def update_life_total(self, user_id:int, new_total:int):
        with self.lock:
            self.cursor.execute(self.config['update']['update_life_totals_by_user_id'], (new_total, user_id))
            self.connection.commit()