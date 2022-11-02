from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('sqlite/booksdb.sdb')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        term = request.form['search']
        return redirect(url_for('search', term=term))
    
    return render_template('home.html')

#search page
@app.route('/search/<term>')
def search(term):
    conn = get_db_connection()
    searchterm="%"+term+"%"
    books = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY title asc', (searchterm, searchterm,)).fetchall()
    conn.close()

    return render_template('search.html', searchterm = term, books=books)

#explore
@app.route('/explore', methods=['POST', 'GET'])
def explore():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY title asc',).fetchall()
    conn.close()

    return render_template('explore.html', books=books)

#add book
@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        add_title = request.form['title']
        add_author = request.form['author']
        add_year = request.form['year']
        add_language = request.form['language']
        add_isbn = request.form['isbn']

        conn = get_db_connection()
        conn.execute('INSERT INTO books (title, author, year_published, language, isbn) VALUES(?,?,?,?,?)', (add_title, add_author, add_year, add_language, add_isbn))
        conn.commit()
        conn.close()

    return render_template('add.html')

#delete book
@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == 'POST':
        remove_id = request.form['remove_id']
        print(remove_id)

        conn = get_db_connection()
        conn.execute('DELETE FROM books WHERE bookid = ?', (remove_id,))
        conn.commit()
        conn.close()
    
    return render_template('delete.html')


@app.route('/borrow/<int:bookid>', methods=['POST', 'GET'])
def borrow(bookid):
    bookid=(int(bookid))

    #print('hi')
    if request.method == 'POST':
        borrow_fname = request.form['fname']
        borrow_lname = request.form['lname']
        borrow_phonenum = request.form['phonenum']
        borrow_address = request.form['address']
        borrow_email = request.form['email']

        conn = get_db_connection()
        conn.execute('INSERT INTO borrowers (fname, lname, phone_number, address, email) VALUES(?,?,?,?,?)', (borrow_fname, borrow_lname, borrow_phonenum, borrow_address, borrow_email,))
        conn.commit()

        search = conn.execute('SELECT borrowerid FROM borrowers WHERE fname = ?', (borrow_fname,))
        borrowerid = search.fetchone()
        int_borrowerid= int(borrowerid[0])
        print(int_borrowerid)

        conn.execute('INSERT INTO books_borrowed(bookid , borrowerid ) VALUES (?,?)', (bookid, int_borrowerid,))
        conn.commit()
        conn.close()


    return render_template('borrow.html', bookid=bookid)

@app.route('/borrowers')
def borrowers():
    conn = get_db_connection()
    borrowers = conn.execute('SELECT * FROM borrowers',).fetchall()
    conn.close()
    
    return render_template('borrowers.html', borrowers=borrowers)

@app.route('/loans')
def loans():

    conn = get_db_connection()
    books_borrowed = conn.execute('SELECT * FROM books_borrowed',).fetchall()
    conn.close()

    return render_template('loans.html', books_borrowed=books_borrowed)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)