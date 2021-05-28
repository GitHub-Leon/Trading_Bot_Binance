import mysql.connector

from src.config import DB_USERNAME, DB_PASSWORD, DB_NAME


def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_NAME
    )
