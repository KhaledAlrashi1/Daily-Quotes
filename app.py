
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
    conn.commit()
    conn.close()

# Home route
@app.route('/')
def home():
    conn = get_db_connection()
    categories = [
        "Prayer", "Gratitude", "Happiness & Fulfilment", "Wisdom", "Human Gifts",
        "Love & Relationships", "Mental Health", "Diet", "Exercise", "Creativity",
        "Character", "Charisma", "Leadership", "Mastery", "Resilience",
        "Career", "Finance", "Networking", "Communication", "Productivity",
    ]
    
    # "Creativity": Innovation, Problem-solving, and Creative Thinking
    # "Resilience": Overcoming Adversity, Coping Strategies, and Stress Management
    # "Productivity": Time Management, Goal Setting, and Focus Techniques

    quotes_data = []
    for category in categories:
        quote = conn.execute(
            'SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT 1',
            (category,)
        ).fetchone()
        if quote:
            quotes_data.append({'text': quote['text'], 'category': quote['category']})
    conn.close()

    shades_of_green = [
        "#66bb6a",  # Medium green
        "#4caf50",  # Slightly darker green
        "#388e3c",  # Dark green
        "#2e7d32",  # Darker green
        "#1b5e20",  # Very dark green
    ]

    return render_template('home.html', quotes=quotes_data, shades_of_green=shades_of_green)

# Route to refresh quotes
@app.route('/refresh')
def refresh_quotes():
    return redirect(url_for('home'))

@app.route('/add', methods=('GET', 'POST'))
def add_quote():
    categories = [
        "Prayer", "Gratitude", "Happiness & Fulfilment", "Wisdom", "Human Gifts",
        "Love & Relationships", "Mental Health", "Diet", "Exercise", "Creativity",
        "Character", "Charisma", "Leadership", "Mastery", "Resilience",
        "Career", "Finance", "Networking", "Communication", "Productivity",
    ]
    
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
    return render_template('add_quote.html', categories=categories)

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_quote(id):
    conn = get_db_connection()
    quote = conn.execute('SELECT * FROM quotes WHERE id = ?', (id,)).fetchone()
    if quote is None:
        conn.close()
        flash('Quote not found.', 'danger')
        return redirect(url_for('home'))
    
    categories = [
        "Prayer", "Gratitude", "Happiness & Fulfilment", "Wisdom", "Human Gifts",
        "Love & Relationships", "Mental Health", "Diet", "Exercise", "Creativity",
        "Character", "Charisma", "Leadership", "Mastery", "Resilience",
        "Career", "Finance", "Networking", "Communication", "Productivity",
    ]

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
    return render_template('edit_quote.html', quote=quote, categories=categories)


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
    # Get query parameters
    per_page = request.args.get('per_page', 10, type=int)
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', '', type=str)


    conn = get_db_connection()

    categories = [
        "Prayer", "Gratitude", "Happiness & Fulfilment", "Wisdom", "Human Gifts",
        "Love & Relationships", "Mental Health", "Diet", "Exercise", "Creativity",
        "Character", "Charisma", "Leadership", "Mastery", "Resilience",
        "Career", "Finance", "Networking", "Communication", "Productivity",
    ]

    # Build the query based on the category filter
    if category_filter and category_filter in categories:
        total_quotes = conn.execute('SELECT COUNT(*) FROM quotes WHERE category = ?', (category_filter,)).fetchone()[0]
        quotes = conn.execute(
            'SELECT * FROM quotes WHERE category = ? LIMIT ? OFFSET ?',
            (category_filter, per_page, (page - 1) * per_page)
        ).fetchall()
    else:
        total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
        quotes = conn.execute('SELECT * FROM quotes LIMIT ? OFFSET ?', (per_page, (page - 1) * per_page)).fetchall()

    total_pages = (total_quotes + per_page - 1) // per_page
    conn.close()

    return render_template(
        'all_quotes.html',
        quotes=quotes,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        categories=categories,
        category_filter=category_filter
    )

@app.route('/quote_counts')
def quote_counts():
    conn = get_db_connection()
    # Total quotes
    total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
    # Quotes per category
    category_counts = conn.execute('SELECT category, COUNT(*) as count FROM quotes GROUP BY category').fetchall()
    conn.close()

    # Convert to dictionary
    counts = {'total': total_quotes, 'categories': {row['category']: row['count'] for row in category_counts}}
    return jsonify(counts)

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

if __name__ == '__main__':
    init_db()
    app.run(debug=True)