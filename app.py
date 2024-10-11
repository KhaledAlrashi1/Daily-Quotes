
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import date
import secrets
from datetime import datetime
import json
import os

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

def load_quote_offset():
    try:
        with open('quote_offset.json', 'r') as f:
            data = json.load(f)
            return data.get('quote_offset', 0), data.get('last_access_date', None)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0, None

def save_quote_offset(offset, last_access_date):
    with open('quote_offset.json', 'w') as f:
        json.dump({'quote_offset': offset, 'last_access_date': last_access_date}, f)

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

    # Load quote_offset and last_access_date from the file
    quote_offset, last_access_date = load_quote_offset()

    today_str = date.today().isoformat()

    # If the date has changed, reset the quote_offset
    if last_access_date != today_str:
        quote_offset = 0
        last_access_date = today_str
        save_quote_offset(quote_offset, last_access_date)
    else:
        # No need to save here if values haven't changed
        pass

    quotes_data = []
    today = date.today()
    fixed_start_date = date(2024, 1, 1)  # Choose a fixed start date
    day_count = (today - fixed_start_date).days

    # Adjust day_count with quote_offset
    adjusted_day_count = day_count + quote_offset

    for category in categories:
        # Fetch all quotes in the category, ordered by ID
        quotes = conn.execute(
            'SELECT * FROM quotes WHERE category = ? ORDER BY id',
            (category,)
        ).fetchall()
        n = len(quotes)
        if n > 0:
            # Calculate the index based on the adjusted day count
            index = adjusted_day_count % n
            quote = quotes[index]
            quotes_data.append({'text': quote['text'], 'category': quote['category']})
        else:
            # No quotes in this category
            pass
    conn.close()

    shades_of_green = [
        "#66bb6a",  # Medium green
        "#4caf50",  # Slightly darker green
        "#388e3c",  # Dark green
        "#2e7d32",  # Darker green
        "#1b5e20",  # Very dark green
    ]

    return render_template('home.html', quotes=quotes_data, shades_of_green=shades_of_green)

@app.route('/next_quotes')
def next_quotes():
    # Load the current quote_offset and last_access_date
    quote_offset, last_access_date = load_quote_offset()
    # Increment the quote_offset
    quote_offset += 1
    # Save the updated quote_offset
    today_str = date.today().isoformat()
    save_quote_offset(quote_offset, last_access_date)
    return redirect(url_for('home'))

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
            'SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT ? OFFSET ?',
            (category_filter, per_page, (page - 1) * per_page)
        ).fetchall()

        # Add the missing total_pages calculation for category filtering
        total_pages = (total_quotes + per_page - 1) // per_page

    else:
        total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
        quotes = conn.execute('SELECT * FROM quotes ORDER BY RANDOM() LIMIT ? OFFSET ?', (per_page, (page - 1) * per_page)).fetchall()

        total_pages = (total_quotes + per_page - 1) // per_page
    
    # Calculate pages to show
    pages_to_show = []

    if total_pages <= 5:
        pages_to_show = list(range(1, total_pages + 1))
    else:
        pages_to_show = []

        # Always show the first page
        pages_to_show.append(1)

        # Determine when to show ellipses
        if page > 3:
            pages_to_show.append('...')

        # Determine the range of page numbers to display around the current page
        if page <= 3:
            pages_to_show.extend([2, 3, 4])
        elif page >= total_pages - 2:
            pages_to_show.extend([total_pages - 3, total_pages - 2, total_pages - 1])
        else:
            pages_to_show.extend([page - 1, page, page + 1])

        # Determine when to show ellipses
        if page < total_pages - 2:
            pages_to_show.append('...')

        # Always show the last page
        pages_to_show.append(total_pages)

    # Remove duplicates and sort the list
    pages_to_show = [x for i, x in enumerate(pages_to_show) if x not in pages_to_show[:i]]

    conn.close()

    shades_of_green = [
        "#66bb6a",  # Medium green
        "#4caf50",  # Slightly darker green
        "#388e3c",  # Dark green
        "#2e7d32",  # Darker green
        "#1b5e20",  # Very dark green
        "#000000"   # Black
    ]

    # Pass shades_of_green to the template
    return render_template(
        'all_quotes.html',
        quotes=quotes,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        categories=categories,
        category_filter=category_filter,
        shades_of_green=shades_of_green,
        pages_to_show=pages_to_show
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