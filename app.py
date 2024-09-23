
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
import os
from werkzeug.utils import secure_filename
import pandas as pd  # If using pandas
import secrets
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('quotes.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Drop existing tables (optional)
    conn.execute('DROP TABLE IF EXISTS quotes')
    # Create quotes table without user_id
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
    ''')
    # Insert initial quotes if the table is empty
    quotes_exist = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
    if not quotes_exist:
        initial_quotes = [
            "The best way to predict the future is to invent it.",
            "Life is 10% what happens to us and 90% how we react to it.",
            "An unexamined life is not worth living.",
            "Eighty percent of success is showing up.",
            "Your time is limited, so don't waste it living someone else's life."
        ]
        conn.executemany('INSERT INTO quotes (text) VALUES (?)', [(q,) for q in initial_quotes])
    conn.commit()
    conn.close()

# Home route
@app.route('/')
def home():
    conn = get_db_connection()
    quotes = conn.execute('SELECT * FROM quotes').fetchall()
    conn.close()
    if len(quotes) < 3:
        displayed_quotes = quotes
    else:
        displayed_quotes = random.sample(quotes, 3)
    return render_template('home.html', quotes=displayed_quotes)

# Route to refresh quotes
@app.route('/refresh')
def refresh_quotes():
    return redirect(url_for('home'))

@app.route('/add', methods=('GET', 'POST'))
def add_quote():
    if request.method == 'POST':
        quote_text = request.form.get('quote')
        if quote_text:
            conn = get_db_connection()
            conn.execute('INSERT INTO quotes (text) VALUES (?)', (quote_text,))
            conn.commit()
            conn.close()
            flash('Quote added successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please enter a quote.', 'danger')
    return render_template('add_quote.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_quote(id):
    conn = get_db_connection()
    quote = conn.execute('SELECT * FROM quotes WHERE id = ?', (id,)).fetchone()
    if quote is None:
        conn.close()
        flash('Quote not found.', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        quote_text = request.form['quote']
        if quote_text:
            conn.execute('UPDATE quotes SET text = ? WHERE id = ?', (quote_text, id))
            conn.commit()
            conn.close()
            flash('Quote updated successfully!', 'success')
            return redirect(url_for('home'))
    conn.close()
    return render_template('edit_quote.html', quote=quote)

@app.route('/delete/<int:id>', methods=('POST',))
def delete_quote(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM quotes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Quote deleted successfully!', 'success')
    return redirect(url_for('home'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            try:
                # Using pandas
                df = pd.read_csv(file.stream, header=None)
                quotes_list = df[0].tolist()
                conn = get_db_connection()
                conn.executemany('INSERT INTO quotes (text) VALUES (?)', [(quote,) for quote in quotes_list])
                conn.commit()
                conn.close()
                flash('Quotes uploaded successfully!', 'success')
            except Exception as e:
                flash(f'Error processing CSV file: {e}', 'danger')
            return redirect(url_for('home'))
        else:
            flash('Allowed file types are CSV.', 'danger')
    return render_template('upload_csv.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)