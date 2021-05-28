from src.config import FREE_PACKAGE_ID
from src.helpers.database_connection import connect_to_database


def check_package(email):
    db = connect_to_database()
    db_cursor = db.cursor()

    query = "select Package_ID from Users where Email like %s"
    db_cursor.execute(query, (email,))
    user_package = db_cursor.fetchone()

    query = "select * from Package where Package_ID like %s"
    db_cursor.execute(query, (user_package,))
    package = db_cursor.fetchone()

    if user_package[0] == FREE_PACKAGE_ID:
        return "free"
    return "no valid package"
