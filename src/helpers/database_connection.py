import mysql.connector

# local dependencies
from src.config import DB_USERNAME, DB_PASSWORD, DB_NAME
from src.helpers.scripts.logger import debug_log, console_log


def connect_to_database():
    debug_log("Create connection to database", False)

    try:
        return mysql.connector.connect(
            host="localhost",
            user=DB_USERNAME,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Exception as e:
        debug_log("Error while trying to connect do database. Error-Message: " + str(e), True)
