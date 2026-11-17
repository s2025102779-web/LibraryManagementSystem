
from config import get_db_connection
from datetime import date


class Loan:

    @staticmethod
    def borrow_book(book_id, member_id):
        conn = get_db_connection()

        if not conn:
            return False

        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT status FROM book WHERE book_id = ?",
                (book_id,)
            )
            book = cursor.fetchone()

            if not book or book[0] != "Available":
                return False

            cursor.execute(
                """
                INSERT INTO loan
                (book_id, member_id, borrow_date, status)
                VALUES (?, ?, ?, 'Borrowed')
                """,
                (book_id, member_id, date.today())
            )

            cursor.execute(
                "UPDATE book SET status = 'Borrowed' WHERE book_id = ?",
                (book_id,)
            )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error borrowing book: {e}")
            return False

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def return_book(loan_id):
        conn = get_db_connection()

        if not conn:
            return False

        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT book_id FROM loan
                WHERE loan_id = ? AND status = 'Borrowed'
                """,
                (loan_id,)
            )
            result = cursor.fetchone()

            if not result:
                return False

            book_id = result[0]

            cursor.execute(
                """
                UPDATE loan
                SET status = 'Returned', return_date = ?
                WHERE loan_id = ?
                """,
                (date.today(), loan_id)
            )

            cursor.execute(
                "UPDATE book SET status = 'Available' WHERE book_id = ?",
                (book_id,)
            )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error returning book: {e}")
            return False

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_loans():
        conn = get_db_connection()

        if not conn:
            return []

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    l.loan_id,
                    l.book_id,
                    l.member_id,
                    l.borrow_date,
                    l.return_date,
                    l.status,
                    b.title AS book_title,
                    m.name AS member_name
                FROM loan l
                LEFT JOIN book b ON l.book_id = b.book_id
                LEFT JOIN member m ON l.member_id = m.member_id
                ORDER BY l.loan_id DESC
            """)

            return cursor.fetchall()

        except Exception as e:
            print(f"Error fetching loans: {e}")
            return []

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def is_book_borrowed(book_id):
        conn = get_db_connection()

        if not conn:
            return False

        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT COUNT(*) FROM loan
                WHERE book_id = ? AND status = 'Borrowed'
                """,
                (book_id,)
            )

            return cursor.fetchone()[0] > 0

        except Exception as e:
            print(f"Error checking book status: {e}")
            return False

        finally:
            cursor.close()
            conn.close()
