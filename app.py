
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash
from models.book import Book
from member import Member
from loan import Loan

app = Flask(__name__)
app.secret_key = "library_secret_key"


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

    available_books = sum(
        1 for book in books if book['status'] == 'Available'
    )

    recent_books = books[:5]
    latest_loans = loans[:5]

    return render_template(
        'dashboard.html',
        total_books=total_books,
        total_members=total_members,
        borrowed_books=borrowed_books,
        available_books=available_books,
        recent_books=recent_books,
        latest_loans=latest_loans
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
            flash("Book is successfully added!", "success")
            return redirect(url_for('index'))

        flash("An error occurred while adding the book.", "danger")

    return render_template('add_book.html')


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


# BORROW BOOK
@app.route('/borrow', methods=['POST'])
def borrow_book():
    book_id = request.form.get('book_id')
    member_id = request.form.get('member_id')

    if book_id and member_id:
        success = Loan.borrow_book(int(book_id), int(member_id))

        if success:
            flash("Book is successfully borrowed!", "success")
        else:
            flash("The book could not be borrowed.", "danger")
    else:
        flash("Please select a book and a member.", "danger")

    
    return redirect(url_for('index'))


# VIEW BORROWED BOOKS
@app.route('/loans')
def loans():
    all_loans = Loan.get_all_loans()
    return render_template('LOANS.HTML', loans=all_loans)


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
