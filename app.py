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
    books = conn.execute('SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY title asc', (searchterm, searchterm,)).fetchall()
    conn.close()
    return render_template('search.html', searchterm = term, books=books)

@app.route('/explore')
def explore():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books ORDER BY title asc',).fetchall()
    conn.close()
    return render_template('explore.html', books=books)

@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        add_title = request.form['title']
        add_author = request.form['author']

        conn = get_db_connection()
        conn.execute('INSERT INTO books (title, author) VALUES(?,?)', (add_title, add_author))
        conn.commit()
        conn.close()

    return render_template('add.html')

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == 'post':
        remover_id = request.form['remove_id']
        
        conn = get_db_connection()
        conn.execute('DELETE FROM books WHERE bookid = ?', (remover_id))
        conn.commit()
        conn.close()
    
    return render_template('delete.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)