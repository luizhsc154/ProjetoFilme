import sqlite3
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)
OMDB_API_KEY = "79f82874"  

def get_db_connection():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            title TEXT PRIMARY KEY,
            rating TEXT,
            cast TEXT,
            awards TEXT,
            poster TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar-filme')
def buscar_filme():
    title = request.args.get('title')
    if not title:
        return jsonify({'error': 'Título não informado'}), 400

    title_clean = title.strip().lower()
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE title = ?', (title_clean,)).fetchone()

    if movie:
        resultado = {
            'title': movie['title'].title(),  
            'rating': movie['rating'],
            'cast': movie['cast'],
            'awards': movie['awards'],
            'poster': movie['poster'] 
        }
        conn.close()
        return jsonify(resultado)

    omdb_url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(omdb_url)
    data = response.json()

    if data.get('Response') == 'False':
        conn.close()
        return jsonify({'error': 'Filme não encontrado'}), 404

    rating = data.get('imdbRating', 'N/A')
    cast = data.get('Actors', 'N/A')
    awards = data.get('Awards', 'N/A')
    poster = data.get('Poster', 'N/A') 

  
    conn.execute(
        'INSERT INTO movies (title, rating, cast, awards, poster) VALUES (?, ?, ?, ?, ?)',
        (title_clean, rating, cast, awards, poster)
    )
    conn.commit()
    conn.close()

    # Retorna o JSON com os dados completos
    return jsonify({
        'title': data.get('Title', title).strip(),
        'rating': rating,
        'cast': cast,
        'awards': awards,
        'poster': poster
    })

if __name__ == '__main__':
    app.run(debug=True)
