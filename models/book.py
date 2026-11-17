
from config import get_db_connection


class Book:

    @staticmethod
    def get_all_books():
        conn = get_db_connection()

        if not conn:
            return []

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM book ORDER BY book_id DESC")
            books = cursor.fetchall()
            return books

        except Exception as e:
            print(f"Error fetching books: {e}")
            return []

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_book_by_id(book_id):
        conn = get_db_connection()

        if not conn:
            return None

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM book WHERE book_id = ?",
                (book_id,)
            )
            return cursor.fetchone()

        except Exception as e:
            print(f"Error finding book: {e}")
            return None

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

    @staticmethod
    def update_book(book_id, title, author, isbn):
        conn = get_db_connection()

        if not conn:
            return False

        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE book SET title = ?, author = ?, isbn = ? WHERE book_id = ?",
                (title, author, isbn, book_id)
            )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error updating book: {e}")
            return False

        finally:
            cursor.close()
            conn.close()
