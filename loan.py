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
            # 1. I-insert ang loan record
            borrow_date = date.today()
            cursor.execute(
                "INSERT INTO loan (book_id, member_id, borrow_date, status) VALUES (%s, %s, %s, 'Borrowed')",
                (book_id, member_id, borrow_date)
            )
            # 2. Baguhin ang status ng libro patungong 'Borrowed'
            cursor.execute(
                "UPDATE book SET status = 'Borrowed' WHERE book_id = %s",
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