from flask import Flask, render_template, request, redirect, url_for, flash
from models.book import Book
from models.member import Member
from models.loan import Loan

app = Flask(_name_)
app.secret_key = "library_secret_key"

@app.route('/')
def index():
    books = Book.get_all_books()
    members = Member.get_all_members()
    return render_template('index.html', books=books, members=members)

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
        else:
            flash("An error occured while adding the book.", "danger")
            
    return render_template('add_book.html')

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
        else:
            flash("An error occured while adding the member.", "danger")
            
    return render_template('add_member.html')

@app.route('/borrow', methods=['POST'])
def borrow_book():
    book_id = request.form.get('book_id')
    member_id = request.form.get('member_id')
    
    if book_id and member_id:
        success = Loan.borrow_book(int(book_id), int(member_id))
        if success:
            flash("Book is successfully borrowed!", "success")
        else:
            flash("The bookcould not be lent.", "danger")
            
    return redirect(url_for('index'))

if _name_ == '_main_':
    app.run(debug=True)