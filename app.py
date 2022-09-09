from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('sqlite/booksdb.sdb')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        search = request.form['search']
        return redirect(url_for('search', term = search))
    
    return render_template('home.html')

@app.route('/search/<term>')
def search(term):
    conn = get_db_connection()
    searchterm="%"+term+"%"
    books = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ?', (searchterm, searchterm,)).fetchall()
    conn.close()
    return render_template('search.html', searchterm = term, books=books)

@app.route('/explore')
def explore():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books',).fetchall()
    conn.close()
    return render_template('explore.html', books=books)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)