# my_app/routes/quotes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import date, datetime
from models import get_db_connection
from utils import load_quote_offset, save_quote_offset

quotes_bp = Blueprint('quotes', __name__)

@quotes_bp.route('/')
def home():
    conn = get_db_connection()
    # Fetch categories from the database
    categories = [row['name'] for row in conn.execute('SELECT name FROM categories ORDER BY "order" ASC').fetchall()]

    # Load quote_offset and last_access_date from the file
    quote_offset, last_access_date = load_quote_offset()

    today_str = date.today().isoformat()

    # If the date has changed, increment the quote_offset
    if last_access_date != today_str:
        quote_offset += 1
        last_access_date = today_str
        save_quote_offset(quote_offset, last_access_date)

    quotes_data = []
    adjusted_day_count = quote_offset

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
    conn.close()

    shades_of_green = [
        "#66bb6a",  # Medium green
        "#4caf50",  # Slightly darker green
        "#388e3c",  # Dark green
        "#2e7d32",  # Darker green
        "#1b5e20",  # Very dark green
    ]

    return render_template('home.html', quotes=quotes_data, shades_of_green=shades_of_green)


@quotes_bp.route('/next_quotes')
def next_quotes():
    # Load the current quote_offset and last_access_date
    quote_offset, last_access_date = load_quote_offset()
    # Increment the quote_offset
    quote_offset += 1
    # Save the updated quote_offset
    save_quote_offset(quote_offset, last_access_date)
    return redirect(url_for('quotes.home'))


@quotes_bp.route('/refresh')
def refresh_quotes():
    return redirect(url_for('quotes.home'))


@quotes_bp.route('/add', methods=('GET', 'POST'))
def add_quote():
    conn = get_db_connection()
    categories = [row['name'] for row in conn.execute('SELECT name FROM categories').fetchall()]
    conn.close()
    
    if request.method == 'POST':
        quotes_list = request.form.getlist('quotes')
        categories_list = request.form.getlist('categories')
        # Remove any empty strings and strip whitespace
        quotes_list = [q.strip() for q in quotes_list if q.strip()]
        categories_list = [c.strip() for c in categories_list if c.strip()]
        if quotes_list and categories_list and len(quotes_list) == len(categories_list):
            conn = get_db_connection()
            # Insert new categories if they don't exist
            for cat in set(categories_list):
                conn.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat,))
            # Insert quotes
            data = list(zip(quotes_list, categories_list))
            conn.executemany('INSERT INTO quotes (text, category) VALUES (?, ?)', data)
            conn.commit()
            conn.close()
            flash(f'{len(quotes_list)} quote(s) added successfully!', 'success')
            return redirect(url_for('quotes.home'))
        else:
            flash('Please enter at least one quote and select a category.', 'danger')
    return render_template('add_quote.html', categories=categories)


@quotes_bp.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit_quote(id):
    conn = get_db_connection()
    quote = conn.execute('SELECT * FROM quotes WHERE id = ?', (id,)).fetchone()
    if quote is None:
        conn.close()
        flash('Quote not found.', 'danger')
        return redirect(url_for('quotes.home'))

    categories = [row['name'] for row in conn.execute('SELECT name FROM categories').fetchall()]
    conn.close()

    if request.method == 'POST':
        quote_text = request.form['quote']
        category = request.form['category']
        if quote_text and category:
            if category not in categories:
                flash('Invalid category selected.', 'danger')
                return redirect(url_for('quotes.edit_quote', id=id))
            conn = get_db_connection()
            conn.execute('UPDATE quotes SET text = ?, category = ? WHERE id = ?', (quote_text, category, id))
            conn.commit()
            conn.close()
            flash('Quote updated successfully!', 'success')
            return redirect(url_for('quotes.all_quotes'))
        else:
            flash('Please enter the quote and select a category.', 'danger')

    return render_template('edit_quote.html', quote=quote, categories=categories)


@quotes_bp.route('/delete/<int:id>', methods=('POST',))
def delete_quote(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM quotes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Quote deleted successfully!', 'success')
    return redirect(url_for('quotes.home'))


@quotes_bp.route('/all_quotes')
def all_quotes():
    per_page = request.args.get('per_page', 10, type=int)
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', '', type=str)

    conn = get_db_connection()
    categories = [row['name'] for row in conn.execute('SELECT name FROM categories').fetchall()]

    if category_filter and category_filter in categories:
        total_quotes = conn.execute('SELECT COUNT(*) FROM quotes WHERE category = ?', (category_filter,)).fetchone()[0]
        quotes = conn.execute('SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT ? OFFSET ?',
                              (category_filter, per_page, (page - 1) * per_page)).fetchall()
    else:
        total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
        quotes = conn.execute('SELECT * FROM quotes ORDER BY RANDOM() LIMIT ? OFFSET ?',
                              (per_page, (page - 1) * per_page)).fetchall()

    total_pages = (total_quotes + per_page - 1) // per_page

    # Pagination logic for "pages_to_show"
    pages_to_show = []
    if total_pages <= 5:
        pages_to_show = list(range(1, total_pages + 1))
    else:
        # Always include first page
        pages_to_show.append(1)
        if page > 3:
            pages_to_show.append('...')
        # Range around current page
        if page <= 3:
            pages_to_show.extend([2, 3, 4])
        elif page >= total_pages - 2:
            pages_to_show.extend([total_pages - 3, total_pages - 2, total_pages - 1])
        else:
            pages_to_show.extend([page - 1, page, page + 1])
        if page < total_pages - 2:
            pages_to_show.append('...')
        # Always include last page
        pages_to_show.append(total_pages)
    # Remove duplicates & sort
    pages_to_show = [x for i, x in enumerate(pages_to_show) if x not in pages_to_show[:i]]

    conn.close()

    shades_of_green = [
        "#66bb6a",
        "#4caf50",
        "#388e3c",
        "#2e7d32",
        "#1b5e20",
        "#000000"
    ]

    return render_template('all_quotes.html',
                           quotes=quotes,
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages,
                           categories=categories,
                           category_filter=category_filter,
                           shades_of_green=shades_of_green,
                           pages_to_show=pages_to_show)


@quotes_bp.route('/quote_counts')
def quote_counts():
    conn = get_db_connection()
    total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
    category_counts = conn.execute('SELECT category, COUNT(*) as count FROM quotes GROUP BY category').fetchall()
    conn.close()

    counts = {
        'total': total_quotes,
        'categories': {row['category']: row['count'] for row in category_counts}
    }
    return jsonify(counts)


# A helper function for Jinja
@quotes_bp.app_template_global()
def get_quote_count(category_name):
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM quotes WHERE category = ?', (category_name,)).fetchone()[0]
    conn.close()
    return count