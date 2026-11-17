
from config import get_db_connection

class Member:
    @staticmethod
    def add_member(name, email, phone):
        conn = get_db_connection()

        if not conn:
            return False

        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO member (name, email, phone) VALUES (?, ?, ?)",
                (name, email, phone)
            )

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error adding member: {e}")
            return False

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_members():
        conn = get_db_connection()

        if not conn:
            return []

        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM member")
            members = cursor.fetchall()
            return members

        except Exception as e:
            print(f"Error fetching members: {e}")
            return []

        finally:
            cursor.close()
            conn.close()
