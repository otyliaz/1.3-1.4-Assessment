from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date, timedelta

app = Flask(__name__)

today = date.today()

#CONNECTS DATABASE
def get_db_connection():
    conn = sqlite3.connect('sqlite/booksdb.sdb')
    conn.row_factory = sqlite3.Row
    return conn

#HOME PAGE
@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST': #IF A FORM IS SENT USING POST,,
        term = request.form['search']
        return redirect(url_for('search', term=term))
    
    return render_template('home.html')

#SEARCH PAGE
@app.route('/search/<term>')
def search(term):
    conn = get_db_connection()
    searchterm="%"+term+"%" #PUTS A SPACE BEFORE AND AFTER THE SEARCH TERM
    #SELECT ALL FROM TABLE: BOOKS
    books = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY title asc', (searchterm, searchterm,)).fetchall()
    conn.close()

    return render_template('search.html', searchterm = term, books=books)

#EXPLORE PAGE
#SIMILAR TO SEARCH PAGE
@app.route('/explore', methods=['POST', 'GET'])
def explore():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY title asc',).fetchall()
    conn.close()

    return render_template('explore.html', books=books)

#ADD A BOOK
@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        #COLLECTS ALL THE INFORMATION FROM THE HTML FORM
        add_title = request.form['title']
        add_author = request.form['author']
        add_year = request.form['year']
        add_language = request.form['language']
        add_isbn = request.form['isbn']

        conn = get_db_connection()
        #INSERT INTO DATABASE
        conn.execute('INSERT INTO books (title, author, year_published, language, isbn) VALUES(?,?,?,?,?)', (add_title, add_author, add_year, add_language, add_isbn))
        conn.commit()
        conn.close()
        
        #IF IT IS INSERTED, SHOW SUCCESS PAGE
        return redirect(url_for('success'))

    return render_template('add.html')

#DELETE A BOOK
@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        #REMOVE A BOOK USING THE id
        remove_id = request.form['remove_id']
        print(remove_id)

        conn = get_db_connection()
        conn.execute('DELETE FROM books WHERE bookid = ?', (remove_id,))
        conn.commit()
        conn.close()

        return redirect(url_for('success'))
    
    return render_template('delete.html')

#BORROW - BORROWER'S DETAILS ARE ADDED HERE
@app.route('/borrow/<int:bookid>', methods=['POST', 'GET'])
def borrow(bookid):
    bookid=(int(bookid))

    #SELECTS THE TITLE OF THE BOOK.
    conn = get_db_connection()
    select = conn.execute('SELECT title FROM books WHERE bookid = ?', (bookid,)).fetchone()
    title=select[0]
    
    if request.method == 'POST':
        #COLLECTS INFORMATION FROM THE FORM
        borrow_fname = request.form['fname']
        borrow_lname = request.form['lname']
        borrow_phonenum = request.form['phonenum']
        borrow_address = request.form['address']
        borrow_email = request.form['email']
        
        #SEARCHES IF THE BORROWER IS ALREADY IN THE DATABASE.
        search = conn.execute('SELECT * FROM borrowers WHERE fname LIKE ? AND lname LIKE ?',(borrow_fname, borrow_lname,)).fetchall()
        rows = len(search)

        #IF THE BORROWER DOES NOT EXIST,
        if rows == 0 :
            #ENTER THEIR DETAILS INTO THE DATABASE
            conn.execute('INSERT INTO borrowers (fname, lname, phone_number, address, email) VALUES(?,?,?,?,?)', (borrow_fname, borrow_lname, borrow_phonenum, borrow_address, borrow_email,))
            conn.commit()

        #SELECT BORROWER id, AND ENTER INTO TABLE: books_borrowed
        borrowerid = conn.execute('SELECT borrowerid FROM borrowers WHERE fname = ? AND lname= ?', (borrow_fname, borrow_lname,)).fetchone()
        int_borrowerid= int(borrowerid[0])
        # print(int_borrowerid)

        today = date.today()

        #RETURN DATE
        return_date = date.today()+timedelta(days=14)
        print(return_date)

        #INSERT ALL INFO INTO TABLE: books_borrowed    
        conn.execute('INSERT INTO books_borrowed(bookid , borrowerid, loan_date, return_date, returned) VALUES (?,?,?,?,0)', (bookid, int_borrowerid, today, return_date))
        conn.commit()
        conn.close()

        #SUCCESS PAGE IF SUCCESSFUL
        return redirect(url_for('success'))

    return render_template('borrow.html', bookid=bookid, title=title)

#BORROWERS PAGE, SHOWS THE LIST OF BORROWERS.
@app.route('/borrowers')
def borrowers():
    conn = get_db_connection()
    borrowers = conn.execute('SELECT * FROM borrowers',).fetchall()
    conn.close()

    return render_template('borrowers.html', borrowers=borrowers)

#LOANS PAGE, SHOWS ALL THE BORROWERS AND THE BOOKS THEY BORROWED.
@app.route('/loans', methods=['POST', 'GET'])
def loans():
    conn = get_db_connection()
    books_borrowed = conn.execute('SELECT books_borrowed.loanid, books.title, books_borrowed.borrowerid, books.bookid, borrowers.fname, borrowers.lname, books_borrowed.loan_date, books_borrowed.return_date FROM books_borrowed JOIN books ON books_borrowed.bookid=books.bookid JOIN borrowers ON books_borrowed.borrowerid=borrowers.borrowerid WHERE books_borrowed.returned=0;',).fetchall()
    
    today=date.today()

    #RETURNING THE BOOK
    if request.method == 'POST':
        form_loanid = request.form['form_loanid']

        conn.execute('UPDATE books_borrowed SET returned = 1 WHERE loanid=?', (form_loanid,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('success'))
        
    return render_template('loans.html', books_borrowed=books_borrowed, today=today)

#SUCCESS PAGE
@app.route('/success')
def success():
    return render_template('success.html')

#404 ERROR PAGE
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#500 ERROR PAGE
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
