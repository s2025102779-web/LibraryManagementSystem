
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import pymysql.cursors

app = Flask(__name__)
app.secret_key = 'library_secret_key_2026'


# =====================================
# DATABASE CONNECTION
# =====================================

def get_db():
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='leaves',
        database='library_db',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )


# =====================================
# DATE FORMAT HELPER
# =====================================

def format_date(value):
    if value is None:
        return None
    return value.strftime('%b %d, %Y')


# =====================================
# DASHBOARD
# =====================================

@app.route('/')
def index():
    conn = get_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT book_id AS id, title, author, isbn, status
                FROM book
                ORDER BY book_id DESC
                LIMIT 5
            """)
            recent_books = cursor.fetchall()

            cursor.execute("""
                SELECT member_id AS id, name, email
                FROM member
                ORDER BY member_id DESC
                LIMIT 5
            """)
            members = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM book")
            total_books = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) AS total FROM member")
            total_members = cursor.fetchone()['total']

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM loan
                WHERE status = 'Borrowed'
            """)
            borrowed_books = cursor.fetchone()['total']

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM loan
                WHERE status = 'Borrowed'
                AND due_date < CURDATE()
            """)
            overdue_books = cursor.fetchone()['total']

            available_books = total_books - borrowed_books

            cursor.execute("""
                SELECT
                    b.title AS book_title,
                    b.author AS author,
                    m.name AS member_name,
                    l.borrow_date AS borrowed_on,
                    l.due_date AS due_on,
                    CASE
                        WHEN l.due_date < CURDATE()
                        THEN 'Overdue'
                        ELSE 'Borrowed'
                    END AS display_status
                FROM loan l
                JOIN book b ON l.book_id = b.book_id
                JOIN member m ON l.member_id = m.member_id
                WHERE l.status = 'Borrowed'
                ORDER BY l.due_date ASC
            """)

            active_loans = cursor.fetchall()

            for loan in active_loans:
                loan['borrowed_on'] = format_date(loan['borrowed_on'])
                loan['due_on'] = format_date(loan['due_on'])

        return render_template(
            'dashboard.html',
            recent_books=recent_books,
            members=members,
            total_books=total_books,
            total_members=total_members,
            borrowed_books=borrowed_books,
            available_books=available_books,
            overdue_books=overdue_books,
            active_loans=active_loans
        )

    finally:
        conn.close()


# =====================================
# BOOK COLLECTION
# =====================================

@app.route('/books')
def books():
    search = request.args.get('search', '').strip()
    conn = get_db()

    try:
        with conn.cursor() as cursor:

            if search:
                cursor.execute("""
                    SELECT book_id AS id, title, author, isbn, status
                    FROM book
                    WHERE title LIKE %s
                    OR author LIKE %s
                    OR isbn LIKE %s
                    ORDER BY book_id DESC
                """, (
                    f'%{search}%',
                    f'%{search}%',
                    f'%{search}%'
                ))
            else:
                cursor.execute("""
                    SELECT book_id AS id, title, author, isbn, status
                    FROM book
                    ORDER BY book_id DESC
                """)

            book_list = cursor.fetchall()

        return render_template(
            'books.html',
            books=book_list,
            search=search
        )

    finally:
        conn.close()


# =====================================
# ADD BOOK
# =====================================

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()

        if not title or not author or not isbn:
            flash('Please complete all book details.', 'error')
            return redirect(url_for('add_book'))

        conn = get_db()

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO book (title, author, isbn, status)
                    VALUES (%s, %s, %s, 'Available')
                """, (title, author, isbn))

            conn.commit()
            flash('Book added successfully!', 'success')

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

        return redirect(url_for('books'))

    return render_template('add_book.html')


# =====================================
# EDIT BOOK
# =====================================

@app.route('/edit-book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    conn = get_db()

    try:
        with conn.cursor() as cursor:

            if request.method == 'POST':
                title = request.form.get('title', '').strip()
                author = request.form.get('author', '').strip()
                isbn = request.form.get('isbn', '').strip()

                if not title or not author or not isbn:
                    flash('Please complete all book details.', 'error')
                    return redirect(url_for('edit_book', id=id))

                cursor.execute("""
                    UPDATE book
                    SET title=%s, author=%s, isbn=%s
                    WHERE book_id=%s
                """, (title, author, isbn, id))

                conn.commit()
                flash('Book updated successfully!', 'success')
                return redirect(url_for('books'))

            cursor.execute("""
                SELECT book_id AS id, title, author, isbn, status
                FROM book
                WHERE book_id=%s
            """, (id,))

            book = cursor.fetchone()

            if not book:
                flash('Book not found.', 'error')
                return redirect(url_for('books'))

        return render_template('edit_book.html', book=book)

    finally:
        conn.close()


# =====================================
# DELETE BOOK
# =====================================


# =====================================
# DELETE BOOK
# =====================================

@app.route('/delete-book/<int:id>', methods=['POST', 'GET'])
def delete_book(id):
    conn = get_db()

    try:
        with conn.cursor() as cursor:

            # Check only active borrowed records
            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM loan
                WHERE book_id=%s
                AND status='Borrowed'
            """, (id,))

            active_loans = cursor.fetchone()['total']

            if active_loans > 0:
                flash(
                    'This book is currently borrowed and cannot be deleted.',
                    'error'
                )
                return redirect(url_for('books'))

            # Delete old loan history first
            cursor.execute("""
                DELETE FROM loan
                WHERE book_id=%s
            """, (id,))

            # Delete the book
            cursor.execute("""
                DELETE FROM book
                WHERE book_id=%s
            """, (id,))

            if cursor.rowcount == 0:
                flash('Book not found.', 'error')
            else:
                flash('Book deleted successfully!', 'success')

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return redirect(url_for('books'))



# =====================================
# ADD MEMBER
# =====================================

@app.route('/add-member', methods=['GET', 'POST'])
def add_member():

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()

        if not name or not email:
            flash('Please enter member name and email.', 'error')
            return redirect(url_for('add_member'))

        conn = get_db()

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO member (name, email)
                    VALUES (%s, %s)
                """, (name, email))

            conn.commit()
            flash('Member registered successfully!', 'success')

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

        return redirect(url_for('index'))

    return render_template('add_member.html')


# =====================================
# DELETE MEMBER
# =====================================

@app.route('/delete-member/<int:id>', methods=['POST'])
def delete_member(id):
    conn = get_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM loan
                WHERE member_id=%s
            """, (id,))

            if cursor.fetchone()['total'] > 0:
                flash(
                    'Cannot delete this member because they have borrowing records.',
                    'error'
                )
                return redirect(url_for('index'))

            cursor.execute("""
                DELETE FROM member
                WHERE member_id=%s
            """, (id,))

            if cursor.rowcount == 0:
                flash('Member not found.', 'error')
            else:
                flash('Member deleted successfully!', 'success')

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return redirect(url_for('index'))


# =====================================
# BORROW BOOK
# =====================================

@app.route('/borrow', methods=['GET', 'POST'])
def borrow():

    if request.method == 'POST':
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')

        if not book_id or not member_id:
            flash('Please select a book and a member.', 'error')
            return redirect(url_for('loans'))

        conn = get_db()

        try:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT book_id
                    FROM book
                    WHERE book_id=%s
                    AND status='Available'
                """, (book_id,))
                book = cursor.fetchone()

                cursor.execute("""
                    SELECT member_id
                    FROM member
                    WHERE member_id=%s
                """, (member_id,))
                member = cursor.fetchone()

                if not book or not member:
                    flash('Invalid book or member selection.', 'error')
                    return redirect(url_for('loans'))

                cursor.execute("""
                    SELECT loan_id
                    FROM loan
                    WHERE book_id=%s
                    AND status='Borrowed'
                """, (book_id,))

                if cursor.fetchone():
                    flash('This book is already borrowed.', 'error')
                    return redirect(url_for('loans'))

                cursor.execute("""
                    INSERT INTO loan
                    (book_id, member_id, borrow_date, due_date, status)
                    VALUES (
                        %s, %s, CURDATE(),
                        DATE_ADD(CURDATE(), INTERVAL 7 DAY),
                        'Borrowed'
                    )
                """, (book_id, member_id))

                cursor.execute("""
                    UPDATE book
                    SET status='Borrowed'
                    WHERE book_id=%s
                """, (book_id,))

            conn.commit()

            flash(
                'Book borrowed successfully! Due date is 7 days from today.',
                'success'
            )

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

        return redirect(url_for('loans'))

    return redirect(url_for('loans'))


# =====================================
# BORROWED BOOKS / LOANS
# =====================================

@app.route('/loans')
def loans():
    conn = get_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT b.book_id AS id, b.title, b.author, b.isbn, b.status
                FROM book b
                WHERE b.status='Available'
                ORDER BY b.title ASC
            """)
            available_book_list = cursor.fetchall()

            cursor.execute("""
                SELECT member_id AS id, name, email
                FROM member
                ORDER BY name ASC
            """)
            members = cursor.fetchall()

            cursor.execute("""
                SELECT
                    l.loan_id AS id,
                    b.title AS book_title,
                    b.author AS author,
                    m.name AS member_name,
                    l.borrow_date AS borrow_date,
                    l.due_date AS due_date,
                    l.return_date AS return_date,
                    l.status AS status,
                    CASE
                        WHEN l.status='Borrowed'
                        AND l.due_date < CURDATE()
                        THEN 'Overdue'
                        ELSE l.status
                    END AS display_status
                FROM loan l
                JOIN book b ON l.book_id=b.book_id
                JOIN member m ON l.member_id=m.member_id
                ORDER BY l.loan_id DESC
            """)

            loan_list = cursor.fetchall()

            for loan in loan_list:
                loan['borrow_date'] = format_date(loan['borrow_date'])
                loan['due_date'] = format_date(loan['due_date'])
                loan['return_date'] = format_date(loan['return_date'])

        return render_template(
            'loans.html',
            available_book_list=available_book_list,
            members=members,
            loans=loan_list
        )

    finally:
        conn.close()


# =====================================
# RETURN BOOK
# =====================================

@app.route('/return-book/<int:id>', methods=['POST'])
def return_book(id):
    conn = get_db()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT book_id
                FROM loan
                WHERE loan_id=%s
                AND status='Borrowed'
            """, (id,))

            loan = cursor.fetchone()

            if not loan:
                flash(
                    'Loan not found or book already returned.',
                    'error'
                )
                return redirect(url_for('loans'))

            cursor.execute("""
                UPDATE loan
                SET status='Returned',
                    return_date=CURDATE()
                WHERE loan_id=%s
            """, (id,))

            cursor.execute("""
                UPDATE book
                SET status='Available'
                WHERE book_id=%s
            """, (loan['book_id'],))

        conn.commit()
        flash('Book returned successfully!', 'success')

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

    return redirect(url_for('loans'))


# =====================================
# RUN APPLICATION
# =====================================

if __name__ == '__main__':
    app.run(debug=True)
