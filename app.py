from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


books = [
    {"id": 1, "title": "Noli Me Tangere", "author": "Jose Rizal", "isbn": "12345"},
    {"id": 2, "title": "El Filibusterismo", "author": "Jose Rizal", "isbn": "67890"},
]

@app.route("/")
def dashboard():
    return render_template("dashboard.html", total_books=len(books))

@app.route("/books")
def book_list():
    search = request.args.get("search", "")
    if search:
        filtered = [b for b in books if search.lower() in b["title"].lower()]
    else:
        filtered = books
    return render_template("books.html", books=filtered, search=search)

@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        new_book = {
            "id": len(books) + 1,
            "title": request.form["title"],
            "author": request.form["author"],
            "isbn": request.form["isbn"]
        }
        books.append(new_book)
        return redirect(url_for("book_list"))
    return render_template("add_book.html")

@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if request.method == "POST":
        book["title"] = request.form["title"]
        book["author"] = request.form["author"]
        book["isbn"] = request.form["isbn"]
        return redirect(url_for("book_list"))
    return render_template("edit_book.html", book=book)

if __name__ == "__main__":
    app.run(debug=True)