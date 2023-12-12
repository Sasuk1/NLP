import sqlite3
from sqlite3 import Connection, Cursor
import threading
from threading import Lock

class SQLiteConnectionPool:
    def __init__(self, database_path: str):
        self._database_path = database_path
        self._lock = Lock()
        self._pool = {}

    def get_connection(self) -> Connection:
        thread_id = id(threading.current_thread())
        with self._lock:
            if thread_id not in self._pool:
                self._pool[thread_id] = sqlite3.connect(self._database_path)
            else:
                try:
                    # Attempt to execute a simple query to check if the connection is still alive
                    self._pool[thread_id].execute("SELECT 1").fetchall()
                except sqlite3.ProgrammingError:
                    # Reconnect if the connection is closed
                    self._pool[thread_id] = sqlite3.connect(self._database_path)
            return self._pool[thread_id]

    def close_all_connections(self):
        with self._lock:
            for connection in self._pool.values():
                connection.close()

# Initialize the connection pool
connection_pool = SQLiteConnectionPool('data.db')

# Function to create pageTrackTable
def create_page_visited_table():
    connection = connection_pool.get_connection()
    c = connection.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS pageTrackTable(pagename TEXT,timeOfvisit TIMESTAMP)')
    connection.commit()

# Function to add page visited details
def add_page_visited_details(pagename, timeOfvisit):
    connection = connection_pool.get_connection()
    c = connection.cursor()
    c.execute('INSERT INTO pageTrackTable(pagename, timeOfvisit) VALUES(?, ?)', (pagename, timeOfvisit))
    connection.commit()

# Function to view all page visited details
def view_all_page_visited_details():
    connection = connection_pool.get_connection()
    c = connection.cursor()
    c.execute('SELECT * FROM pageTrackTable')
    data = c.fetchall()
    return data

# Function to create emotionclfTable
def create_emotionclf_table():
    connection = connection_pool.get_connection()
    c = connection.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS emotionclfTable(rawtext TEXT, prediction TEXT, probability NUMBER, timeOfvisit TIMESTAMP)')
    connection.commit()

# Function to add prediction details
def add_prediction_details(rawtext, prediction, probability, time_of_visit):
    connection = connection_pool.get_connection()
    c = connection.cursor()
    c.execute('INSERT INTO emotionclfTable(rawtext, prediction, probability, timeOfvisit) VALUES(?, ?, ?, ?)',
              (rawtext, prediction, probability, time_of_visit))
    connection.commit()

# Function to view all prediction details
def view_all_prediction_details():
    connection = connection_pool.get_connection()
    c = connection.cursor()
    c.execute('SELECT * FROM emotionclfTable')
    data = c.fetchall()
    return data
