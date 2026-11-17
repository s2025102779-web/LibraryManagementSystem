
from config import get_db_connection

class Book:

    @staticmethod
    def get_all_books():
        conn = get_db_connection()
        if not conn:
            return []

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM book")
            books = cursor.fetchall()
            return books

        except Exception as e:
            print(f"Error fetching books: {e}")
            return []

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def add_book(title, author, isbn):
        conn = get_db_connection()
        if not conn:
            return False

        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO book (title, author, isbn) VALUES (?, ?, ?)",
                (title, author, isbn)
            )
            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error adding book: {e}")
            return False

        finally:
            cursor.close()
            conn.close()
