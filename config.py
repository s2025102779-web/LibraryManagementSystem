
import mariadb


def get_db_connection():
    try:
        conn = mariadb.connect(
            host="localhost",
            port=3306,
            user="root",
            password="leaves",
            database="library_db"
        )
        return conn

    except mariadb.Error as e:
        print(f"Database connection error: {e}")
        return None
