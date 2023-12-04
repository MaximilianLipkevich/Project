from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_database():
    search_term = request.form.get('search_term')
    conn = sqlite3.connect('films.db')
    cursor = conn.cursor()

    query = f"SELECT * FROM films WHERE film_name LIKE '%{search_term}%'"
    cursor.execute(query)

    results = cursor.fetchall()

    conn.close()

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
