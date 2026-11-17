from flask import Flask, render_template, request, redirect, flash
from loan import borrow_book, return_book, get_all_loans, is_book_borrowed

app = Flask(__name__)
app.secret_key = "library-secret"

books = [
    {"id": 1, "title": "Noli Me Tangere", "author": "Jose Rizal"},
    {"id": 2, "title": "El Filibusterismo", "author": "Jose Rizal"},
    {"id": 3, "title": "Harry Potter", "author": "J.K. Rowling"},
]

@app.route("/")
def dashboard():
    return render_template("dashboard.html", total_books=len(books))

@app.route("/books")
def book_list():
    q = request.args.get("q", "").lower()
    if q:
        filtered = [b for b in books if q in b["title"].lower() or q in b["author"].lower()]
    else:
        filtered = books
    return render_template("book_list.html", books=filtered, q=q)

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        if not title or not author:
            flash("Please fill in all fields!")
            return redirect("/add_book")
        new_id = max([b["id"] for b in books], default=0) + 1
        books.append({"id": new_id, "title": title, "author": author})
        flash("Book added successfully!")
        return redirect("/books")
    return render_template("add_book.html")

@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        flash("Book not found!")
        return redirect("/books")
    if request.method == "POST":
        book["title"] = request.form.get("title")
        book["author"] = request.form.get("author")
        flash("Book updated successfully!")
        return redirect("/books")
    return render_template("edit_book.html", book=book)

@app.route("/delete/<int:book_id>")
def delete_book(book_id):
    global books
    books = [b for b in books if b["id"] != book_id]
    flash("Book deleted!")
    return redirect("/books")

@app.route("/borrow/<int:book_id>", methods=["GET", "POST"])
def borrow(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        flash("Book not found!")
        return redirect("/books")
    if is_book_borrowed(book_id):
        flash("Book is already borrowed!")
        return redirect("/books")
    if request.method == "POST":
        member_name = request.form.get("member_name")
        if not member_name:
            flash("Please enter member name!")
            return redirect(f"/borrow/{book_id}")
        borrow_book(book_id, member_name)
        flash(f"Book borrowed by {member_name}!")
        return redirect("/loans")
    return render_template("borrow.html", book=book)

@app.route("/loans")
def loan_list():
    all_loans = get_all_loans()
    for loan in all_loans:
        book = next((b for b in books if b["id"] == loan["book_id"]), None)
        loan["book_title"] = book["title"] if book else "Unknown"
    return render_template("loans.html", loans=all_loans)

@app.route("/return/<int:loan_id>")
def return_loan(loan_id):
    result = return_book(loan_id)
    if result:
        flash("Book returned successfully!")
    else:
        flash("Loan not found!")
    return redirect("/loans")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)