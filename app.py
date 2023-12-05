from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import logging
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(filename='user_activity.log', level=logging.INFO)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'C:\\Users\\krave\\Documents\\flaskProject\\films.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists!')
            return redirect(url_for('register'))
        finally:
            conn.close()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password!')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/films', methods=['GET', 'POST'])
def films():
    conn = get_db_connection()
    
    if request.method == 'POST':
        search_query = request.form['search_term']
        query = "SELECT * FROM films WHERE film_name LIKE ? OR director LIKE ?"
        films = conn.execute(query, ('%' + search_query + '%', '%' + search_query + '%')).fetchall()
    else:
        query = "SELECT * FROM films"
        films = conn.execute(query).fetchall()
    
    conn.close()
    return render_template('films.html', films=films)



@app.route('/add_to_favorites/<int:film_id>', methods=['POST'])
def add_to_favorites(film_id):
    if 'user_id' not in session:
        flash('You need to be logged in to add favorites')
        return redirect(url_for('login'))

    conn = get_db_connection()
    try:
        exists = conn.execute('SELECT * FROM favorites WHERE user_id = ? AND film_id = ?', (session['user_id'], film_id)).fetchone()
        if not exists:
            conn.execute('INSERT INTO favorites (user_id, film_id) VALUES (?, ?)', (session['user_id'], film_id))
            conn.commit()
            flash('Film added to favorites')
        else:
            flash('Film is already in favorites')
    except sqlite3.Error as e:
        flash('Error adding film to favorites: ' + str(e))
    finally:
        conn.close()

    return redirect(url_for('films'))


@app.route('/my_favorites')
def my_favorites():
    if 'user_id' not in session:
        flash('You need to be logged in to view favorites')
        return redirect(url_for('login'))

    conn = get_db_connection()
    query = """
    SELECT f.* FROM films f
    JOIN favorites fav ON f.id = fav.film_id
    WHERE fav.user_id = ?
    """
    films = conn.execute(query, (session['user_id'],)).fetchall()
    conn.close()
    return render_template('favorites.html', films=films)





@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    favorites = conn.execute('''
        SELECT f.* FROM films f
        JOIN favorites fav ON f.id = fav.film_id
        WHERE fav.user_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()

    return render_template('profile.html', username=session['username'], favorites=favorites)




if __name__ == '__main__':
    app.run(debug=True)
