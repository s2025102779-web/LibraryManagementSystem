import sys
import os
import pymysql  # <-- Pinalitan natin ang mysql.connector ng pymysql

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash
from models.book import Book
from member import Member
from loan import Loan

app = Flask(__name__)
app.secret_key = "library_secret_key"

# HELPER PARA SA DATABASE CONNECTION (Gamit ang PyMySQL)
def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="library_db",  # Palitan kung iba ang pangalan ng database mo
        cursorclass=pymysql.cursors.DictCursor  # Para automatic dictionary ang makuha sa queries
    )

# DASHBOARD
@app.route('/')
def index():
    books = Book.get_all_books()
    members = Member.get_all_members()
    loans = Loan.get_all_loans()

    total_books = len(books)
    total_members = len(members)

    borrowed_books = sum(
        1 for loan in loans if loan['status'] == 'Borrowed'
    )

    available_book_list = [
        book for book in books
        if book['status'] == 'Available'
    ]

    available_books = len(available_book_list)

    recent_books = books[:5]
    recent_loans = loans[:5]

    return render_template(
        'dashboard.html',
        total_books=total_books,
        total_members=total_members,
        borrowed_books=borrowed_books,
        available_books=available_books,
        available_book_list=available_book_list,
        members=members,
        recent_books=recent_books,
        recent_loans=recent_loans
    )


# VIEW BOOKS
@app.route('/books')
def books():
    all_books = Book.get_all_books()
    search = request.args.get('search', '').strip()

    if search:
        books = [
            book for book in all_books
            if search.lower() in book['title'].lower()
            or search.lower() in book['author'].lower()
            or search.lower() in str(book['isbn']).lower()
        ]
    else:
        books = all_books

    return render_template(
        'books.html',
        books=books,
        search=search
    )


# ADD BOOK
@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')

        success = Book.add_book(title, author, isbn)

        if success:
            flash("Book successfully added!", "success")
            return redirect(url_for('books'))

        flash("Unable to add book.", "danger")

    return render_template('add_book.html')


# EDIT BOOK
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.get_book_by_id(book_id)

    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('books'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')

        success = Book.update_book(book_id, title, author, isbn)

        if success:
            flash("Book successfully updated!", "success")
            return redirect(url_for('books'))

        flash("Unable to update book.", "danger")

    return render_template('edit_book.html', book=book)


# DELETE BOOK (SAFE DELETE)
@app.route('/delete-book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # I-check kung kasalukuyang hinihiram pa ang libro
        cursor.execute("SELECT * FROM loans WHERE book_id = %s AND status = 'Borrowed'", (book_id,))
        active_loan = cursor.fetchone()

        if active_loan:
            flash("Cannot delete this book because it is currently borrowed!", "danger")
        else:
            cursor.execute("DELETE FROM loans WHERE book_id = %s", (book_id,))
            cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            conn.commit()
            flash("Book successfully deleted!", "success")

        cursor.close()
        conn.close()
    except Exception as e:
        flash(f"Error deleting book: {e}", "danger")

    return redirect(request.referrer or url_for('index'))


# ADD MEMBER
@app.route('/add-member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        success = Member.add_member(name, email, phone)

        if success:
            flash("Member is successfully added!", "success")
            return redirect(url_for('index'))

        flash("An error occurred while adding the member.", "danger")

    return render_template('add_member.html')


# DELETE MEMBER (SAFE DELETE)
@app.route('/delete-member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # I-check kung may hinihiram pang libro ang member
        cursor.execute("SELECT * FROM loans WHERE member_id = %s AND status = 'Borrowed'", (member_id,))
        active_loan = cursor.fetchone()

        if active_loan:
            flash("Cannot delete this member because they still have a borrowed book!", "danger")
        else:
            cursor.execute("DELETE FROM loans WHERE member_id = %s", (member_id,))
            cursor.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
            conn.commit()
            flash("Member successfully deleted!", "success")

        cursor.close()
        conn.close()
    except Exception as e:
        flash(f"Error deleting member: {e}", "danger")

    return redirect(request.referrer or url_for('index'))


# BORROW BOOK
@app.route('/borrow', methods=['POST'])
def borrow_book():
    book_id = request.form.get('book_id')
    member_id = request.form.get('member_id')

    if book_id and member_id:
        success = Loan.borrow_book(int(book_id), int(member_id))

        if success:
            flash("Book successfully borrowed!", "success")
        else:
            flash("The book could not be borrowed.", "danger")
    else:
        flash("Please select a book and a member.", "danger")

    return redirect(url_for('loans'))


# VIEW BORROWED BOOKS
@app.route('/loans')
def loans():
    all_loans = Loan.get_all_loans()
    all_books = Book.get_all_books()
    all_members = Member.get_all_members()

    available_book_list = [
        book for book in all_books
        if book['status'] == 'Available'
    ]

    return render_template(
        'LOANS.HTML',
        loans=all_loans,
        available_book_list=available_book_list,
        members=all_members
    )


# RETURN BOOK
@app.route('/return/<int:loan_id>')
def return_book(loan_id):
    success = Loan.return_book(loan_id)

    if success:
        flash("Book successfully returned!", "success")
    else:
        flash("Unable to return this book.", "danger")

    return redirect(url_for('loans'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)