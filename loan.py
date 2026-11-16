loans = []
loan_id_counter = 1

def borrow_book(book_id, member_name):
    global loan_id_counter
    for loan in loans:
        if loan["book_id"] == book_id and loan["status"] == "Borrowed":
            return None
    new_loan = {
        "id": loan_id_counter,
        "book_id": book_id,
        "member_name": member_name,
        "status": "Borrowed"
    }
    loans.append(new_loan)
    loan_id_counter += 1
    return new_loan

def return_book(loan_id):
    for loan in loans:
        if loan["id"] == loan_id:
            loan["status"] = "Returned"
            return loan
    return None

def get_all_loans():
    return loans

def is_book_borrowed(book_id):
    for loan in loans:
        if loan["book_id"] == book_id and loan["status"] == "Borrowed":
            return True
    return False