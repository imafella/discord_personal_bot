import sqlite3
from Utils import General_Utils as utility




class DatabaseConnection:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.config = utility.load_json("db_config")
        # self.setup_database()

    def connect(self):
        # Connect to the SQLite database (or create it if it doesn't exist)
        if self.connection == None:
            self.connection = sqlite3.connect(self.db_name)
        # Create a cursor object to interact with the database
        if self.cursor == None:
            self.cursor = self.connection.cursor()

    def close(self):
        # Close the database connection
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None


    # def setup_database(self):
    #     self.connect()
    #     # Create the tables if it doesn't exist
    #     for script in self.config["create"].values():
    #         self.cursor.execute(script)
    #     # Commit the changes and close the connection
    #     self.connection.commit()
    #     self.close()
    #     # Close the connection
