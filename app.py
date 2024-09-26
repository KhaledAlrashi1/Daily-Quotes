
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import random
import os
from werkzeug.utils import secure_filename
import pandas as pd  # If using pandas
import secrets
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('quotes.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Create the quotes table with a 'category' column
    conn.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    # Insert initial quotes if the table is empty
    quotes_exist = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
    if not quotes_exist:
        initial_quotes = [
            ("The best way to predict the future is to invent it.", "Career"),
            ("Life is 10% what happens to us and 90% how we react to it.", "Mastery"),
            ("An unexamined life is not worth living.", "Charisma"),
            ("Eighty percent of success is showing up.", "Career"),
            ("Your time is limited, so don't waste it living someone else's life.", "Mastery"),
            ("Invest in yourself. Your career is the engine of your wealth.", "Finance"),
            ("Health is the greatest gift, contentment the greatest wealth, faithfulness the best relationship.", "Diet"),
            ("Happiness depends upon ourselves.", "Happiness & Fulfilment"),
            ("Character is how you treat those who can do nothing for you.", "Character"),
            ("Prayer is the key of the morning and the bolt of the evening.", "Prayer"),
            ("Gratitude turns what we have into enough.", "Gratitude")
        ]
        conn.executemany('INSERT INTO quotes (text, category) VALUES (?, ?)', initial_quotes)
    conn.commit()
    conn.close()

# Home route
@app.route('/')
def home():
    conn = get_db_connection()
    categories = [
        "Finance", "Diet", "Exercise", "Career", "Relationships", "Charisma", "Mastery",
        "Happiness & Fulfilment", "Character", "Prayer", "Gratitude"
    ]
    quotes = []
    for category in categories:
        quote = conn.execute(
            'SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT 1',
            (category,)
        ).fetchone()
        if quote:
            quotes.append(quote)
    conn.close()
    return render_template('home.html', quotes=quotes)

# Route to refresh quotes
@app.route('/refresh')
def refresh_quotes():
    return redirect(url_for('home'))

@app.route('/add', methods=('GET', 'POST'))
def add_quote():
    if request.method == 'POST':
        # Retrieve all quote inputs and categories from the form
        quotes_list = request.form.getlist('quotes')
        categories_list = request.form.getlist('categories')
        # Remove any empty strings and strip whitespace
        quotes_list = [quote.strip() for quote in quotes_list if quote.strip()]
        categories_list = [category.strip() for category in categories_list if category.strip()]
        if quotes_list and categories_list and len(quotes_list) == len(categories_list):
            conn = get_db_connection()
            # Prepare data for insertion
            data = [(quote, category) for quote, category in zip(quotes_list, categories_list)]
            conn.executemany('INSERT INTO quotes (text, category) VALUES (?, ?)', data)
            conn.commit()
            conn.close()
            flash(f'{len(quotes_list)} quote(s) added successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Please enter at least one quote and select a category.', 'danger')
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
        category = request.form['category']
        if quote_text and category:
            conn.execute('UPDATE quotes SET text = ?, category = ? WHERE id = ?', (quote_text, category, id))
            conn.commit()
            conn.close()
            flash('Quote updated successfully!', 'success')
            return redirect(url_for('all_quotes'))
        else:
            flash('Please enter the quote and select a category.', 'danger')
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

# Route to display all quotes
@app.route('/all_quotes')
def all_quotes():
    # Get the 'per_page' parameter from the query string, default to 10
    per_page = request.args.get('per_page', 10, type=int)
    # Get the 'page' parameter from the query string, default to 1
    page = request.args.get('page', 1, type=int)

    conn = get_db_connection()
    # Get total number of quotes
    total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
    # Calculate total pages
    total_pages = (total_quotes + per_page - 1) // per_page

    # Fetch quotes for the current page
    quotes = conn.execute('SELECT * FROM quotes LIMIT ? OFFSET ?', (per_page, (page - 1) * per_page)).fetchall()
    conn.close()

    return render_template('all_quotes.html', quotes=quotes, page=page, per_page=per_page, total_pages=total_pages)
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

if __name__ == '__main__':
    init_db()
    app.run(debug=True)