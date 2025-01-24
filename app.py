
# from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
# import sqlite3
# from datetime import date
# import secrets
# from datetime import datetime
# import json
# import os

# app = Flask(__name__)
# app.secret_key = secrets.token_hex(32)

# # Function to get a database connection
# def get_db_connection():
#     conn = sqlite3.connect('quotes.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# def init_db():
#     conn = get_db_connection()
#     # Create the quotes table with a 'category' column
#     conn.execute('''
#         CREATE TABLE IF NOT EXISTS quotes (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             text TEXT NOT NULL,
#             category TEXT NOT NULL
#         )
#     ''')

#     # Create the categories table with an 'order' column
#     conn.execute('''
#         CREATE TABLE IF NOT EXISTS categories (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL UNIQUE,
#             "order" INTEGER
#         )
#     ''')

#     # Ensure the "Others" category exists
#     conn.execute('''
#         INSERT OR IGNORE INTO categories (name) VALUES (?)
#     ''', ("Others",))

#     # Check if 'order' column exists in 'categories' table
#     cursor = conn.execute("PRAGMA table_info(categories)")
#     columns = [column[1] for column in cursor.fetchall()]
#     if 'order' not in columns:
#         conn.execute('ALTER TABLE categories ADD COLUMN "order" INTEGER')
#         # Initialize order values
#         conn.execute('UPDATE categories SET "order" = id')
    
#     conn.commit()
#     conn.close()


# """ 
# Exporting Your Quotes:
# 1.	Open the SQLite Command-Line Interface:
#     sqlite3 quotes.db

# 2. Export to CSV
#     a. .headers on
#     b. .mode csv
#     c. .output quotes_export.csv
#     d. SELECT * FROM quotes;
#     e. .quit
# """

# """
# Importing from CSV:
# 1. Open the SQLite Command-Line Interface:
#     sqlite3 quotes.db

# 2. 	Import the CSV Data:
#     a. .mode csv
#     b. .import quotes_export.csv quotes
#     c. .quit
# """

# def load_quote_offset():
#     try:
#         with open('quote_offset.json', 'r') as f:
#             data = json.load(f)
#             return data.get('quote_offset', 0), data.get('last_access_date', None)
#     except (FileNotFoundError, json.JSONDecodeError):
#         return 0, None

# def save_quote_offset(offset, last_access_date):
#     with open('quote_offset.json', 'w') as f:
#         json.dump({'quote_offset': offset, 'last_access_date': last_access_date}, f)


# @app.route('/')
# def home():
#     conn = get_db_connection()
#     # Fetch categories from the database
#     categories = [row['name'] for row in conn.execute('SELECT name FROM categories ORDER BY "order" ASC').fetchall()]

#     # Load quote_offset and last_access_date from the file
#     quote_offset, last_access_date = load_quote_offset()

#     today_str = date.today().isoformat()

#     # If the date has changed, reset the quote_offset
#     if last_access_date != today_str:
#         quote_offset += 1
#         last_access_date = today_str
#         save_quote_offset(quote_offset, last_access_date)

#     quotes_data = []
#     adjusted_day_count = quote_offset

#     for category in categories:
#         # Fetch all quotes in the category, ordered by ID
#         quotes = conn.execute(
#             'SELECT * FROM quotes WHERE category = ? ORDER BY id',
#             (category,)
#         ).fetchall()
#         n = len(quotes)
#         if n > 0:
#             # Calculate the index based on the adjusted day count
#             index = adjusted_day_count % n
#             quote = quotes[index]
#             quotes_data.append({'text': quote['text'], 'category': quote['category']})
#         else:
#             # No quotes in this category
#             pass
#     conn.close()

#     shades_of_green = [
#         "#66bb6a",  # Medium green
#         "#4caf50",  # Slightly darker green
#         "#388e3c",  # Dark green
#         "#2e7d32",  # Darker green
#         "#1b5e20",  # Very dark green
#     ]

#     return render_template('home.html', quotes=quotes_data, shades_of_green=shades_of_green)

# @app.route('/next_quotes')
# def next_quotes():
#     # Load the current quote_offset and last_access_date
#     quote_offset, last_access_date = load_quote_offset()
#     # Increment the quote_offset
#     quote_offset += 1
#     # # Save the updated quote_offset
#     # today_str = date.today().isoformat()
#     save_quote_offset(quote_offset, last_access_date)
#     return redirect(url_for('home'))

# # Route to refresh quotes
# @app.route('/refresh')
# def refresh_quotes():
#     return redirect(url_for('home'))

# @app.route('/add', methods=('GET', 'POST'))
# def add_quote():
#     conn = get_db_connection()
#     categories = [row['name'] for row in conn.execute('SELECT name FROM categories').fetchall()]
#     conn.close()
    
#     if request.method == 'POST':
#         # Retrieve all quote inputs and categories from the form
#         quotes_list = request.form.getlist('quotes')
#         categories_list = request.form.getlist('categories')
#         # Remove any empty strings and strip whitespace
#         quotes_list = [quote.strip() for quote in quotes_list if quote.strip()]
#         categories_list = [category.strip() for category in categories_list if category.strip()]
#         if quotes_list and categories_list and len(quotes_list) == len(categories_list):
#             conn = get_db_connection()
#             # Insert new categories if they don't exist
#             for category in set(categories_list):
#                 conn.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
#             # Prepare data for insertion
#             data = [(quote, category) for quote, category in zip(quotes_list, categories_list)]
#             conn.executemany('INSERT INTO quotes (text, category) VALUES (?, ?)', data)
#             conn.commit()
#             conn.close()
#             flash(f'{len(quotes_list)} quote(s) added successfully!', 'success')
#             return redirect(url_for('home'))
#         else:
#             flash('Please enter at least one quote and select a category.', 'danger')
#     return render_template('add_quote.html', categories=categories)

# @app.route('/edit/<int:id>', methods=('GET', 'POST'))
# def edit_quote(id):
#     conn = get_db_connection()
#     quote = conn.execute('SELECT * FROM quotes WHERE id = ?', (id,)).fetchone()
#     if quote is None:
#         conn.close()
#         flash('Quote not found.', 'danger')
#         return redirect(url_for('home'))

#     categories = [row['name'] for row in conn.execute('SELECT name FROM categories').fetchall()]
#     conn.close()

#     if request.method == 'POST':
#         quote_text = request.form['quote']
#         category = request.form['category']
#         if quote_text and category:
#             if category not in categories:
#                 flash('Invalid category selected.', 'danger')
#                 return redirect(url_for('edit_quote', id=id))
#             conn = get_db_connection()
#             conn.execute('UPDATE quotes SET text = ?, category = ? WHERE id = ?', (quote_text, category, id))
#             conn.commit()
#             conn.close()
#             flash('Quote updated successfully!', 'success')
#             return redirect(url_for('all_quotes'))
#         else:
#             flash('Please enter the quote and select a category.', 'danger')

#     return render_template('edit_quote.html', quote=quote, categories=categories)


# @app.route('/delete/<int:id>', methods=('POST',))
# def delete_quote(id):
#     conn = get_db_connection()
#     conn.execute('DELETE FROM quotes WHERE id = ?', (id,))
#     conn.commit()
#     conn.close()
#     flash('Quote deleted successfully!', 'success')
#     return redirect(url_for('home'))

# # Route to display all quotes
# @app.route('/all_quotes')
# def all_quotes():
#     # Get query parameters
#     per_page = request.args.get('per_page', 10, type=int)
#     page = request.args.get('page', 1, type=int)
#     category_filter = request.args.get('category', '', type=str)

#     conn = get_db_connection()

#     categories = [row['name'] for row in conn.execute('SELECT name FROM categories').fetchall()]

#     # Build the query based on the category filter
#     if category_filter and category_filter in categories:
#         total_quotes = conn.execute('SELECT COUNT(*) FROM quotes WHERE category = ?', (category_filter,)).fetchone()[0]
#         quotes = conn.execute(
#             'SELECT * FROM quotes WHERE category = ? ORDER BY RANDOM() LIMIT ? OFFSET ?',
#             (category_filter, per_page, (page - 1) * per_page)
#         ).fetchall()

#         total_pages = (total_quotes + per_page - 1) // per_page

#     else:
#         total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
#         quotes = conn.execute('SELECT * FROM quotes ORDER BY RANDOM() LIMIT ? OFFSET ?', (per_page, (page - 1) * per_page)).fetchall()

#         total_pages = (total_quotes + per_page - 1) // per_page
    
#     # Calculate pages to show
#     pages_to_show = []

#     if total_pages <= 5:
#         pages_to_show = list(range(1, total_pages + 1))
#     else:
#         pages_to_show = []

#         # Always show the first page
#         pages_to_show.append(1)

#         # Determine when to show ellipses
#         if page > 3:
#             pages_to_show.append('...')

#         # Determine the range of page numbers to display around the current page
#         if page <= 3:
#             pages_to_show.extend([2, 3, 4])
#         elif page >= total_pages - 2:
#             pages_to_show.extend([total_pages - 3, total_pages - 2, total_pages - 1])
#         else:
#             pages_to_show.extend([page - 1, page, page + 1])

#         # Determine when to show ellipses
#         if page < total_pages - 2:
#             pages_to_show.append('...')

#         # Always show the last page
#         pages_to_show.append(total_pages)

#     # Remove duplicates and sort the list
#     pages_to_show = [x for i, x in enumerate(pages_to_show) if x not in pages_to_show[:i]]

#     conn.close()

#     shades_of_green = [
#         "#66bb6a",  # Medium green
#         "#4caf50",  # Slightly darker green
#         "#388e3c",  # Dark green
#         "#2e7d32",  # Darker green
#         "#1b5e20",  # Very dark green
#         "#000000"   # Black
#     ]

#     # Pass shades_of_green to the template
#     return render_template(
#         'all_quotes.html',
#         quotes=quotes,
#         page=page,
#         per_page=per_page,
#         total_pages=total_pages,
#         categories=categories,
#         category_filter=category_filter,
#         shades_of_green=shades_of_green,
#         pages_to_show=pages_to_show
#     )

# @app.route('/quote_counts')
# def quote_counts():
#     conn = get_db_connection()
#     # Total quotes
#     total_quotes = conn.execute('SELECT COUNT(*) FROM quotes').fetchone()[0]
#     # Quotes per category
#     category_counts = conn.execute('SELECT category, COUNT(*) as count FROM quotes GROUP BY category').fetchall()
#     conn.close()

#     # Convert to dictionary
#     counts = {'total': total_quotes, 'categories': {row['category']: row['count'] for row in category_counts}}
#     return jsonify(counts)

# @app.context_processor
# def inject_current_year():
#     return {'current_year': datetime.utcnow().year}

# @app.route('/categories', methods=['GET', 'POST'])
# def manage_categories():
#     conn = get_db_connection()
#     if request.method == 'POST':
#         if 'update_order' in request.form:
#             # Handle updating the order of categories
#             orders = request.form.getlist('order')
#             ids = request.form.getlist('id')
#             for id, order in zip(ids, orders):
#                 conn.execute('UPDATE categories SET "order" = ? WHERE id = ?', (int(order), int(id)))
#             conn.commit()
#             flash('Category order updated successfully!', 'success')
#             conn.close()
#             return redirect(url_for('manage_categories'))
#         elif 'add_category' in request.form:
#             # Handle adding a new category
#             category_name = request.form.get('category_name').strip()
#             quote_text = request.form.get('quote_text').strip()
#             if category_name and quote_text:
#                 try:
#                     # Determine the next order value
#                     max_order = conn.execute('SELECT MAX("order") FROM categories').fetchone()[0]
#                     if max_order is None:
#                         max_order = 0
#                     next_order = max_order + 1
#                     # Insert the new category with the next order value
#                     conn.execute('INSERT INTO categories (name, "order") VALUES (?, ?)', (category_name, next_order))
#                     # Insert the new quote with the new category
#                     conn.execute('INSERT INTO quotes (text, category) VALUES (?, ?)', (quote_text, category_name))
#                     conn.commit()
#                     flash('Category and quote added successfully!', 'success')
#                 except sqlite3.IntegrityError:
#                     flash('Category already exists.', 'danger')
#                 conn.close()
#                 return redirect(url_for('manage_categories'))
#             else:
#                 flash('Please enter both category name and at least one quote.', 'danger')
#                 conn.close()
#                 return redirect(url_for('manage_categories'))
#     else:
#         # Display the list of categories ordered by 'order'
#         categories = conn.execute('SELECT * FROM categories ORDER BY "order" ASC').fetchall()
#         conn.close()
#         return render_template('categories.html', categories=categories)
    
# @app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
# def edit_category(id):
#     conn = get_db_connection()
#     category = conn.execute('SELECT * FROM categories WHERE id = ?', (id,)).fetchone()
#     if not category:
#         conn.close()
#         flash('Category not found.', 'danger')
#         return redirect(url_for('manage_categories'))

#     if request.method == 'POST':
#         new_name = request.form.get('category_name').strip()
#         if new_name:
#             try:
#                 # Update the category name in categories table
#                 conn.execute('UPDATE categories SET name = ? WHERE id = ?', (new_name, id))
#                 # Update the category name in quotes table
#                 conn.execute('UPDATE quotes SET category = ? WHERE category = ?', (new_name, category['name']))
#                 conn.commit()
#                 flash('Category updated successfully!', 'success')
#             except sqlite3.IntegrityError:
#                 flash('Category name already exists.', 'danger')
#             conn.close()
#             return redirect(url_for('manage_categories'))
#         else:
#             flash('Please enter a category name.', 'danger')
#     conn.close()
#     return render_template('edit_category.html', category=category)

# @app.route('/delete_category/<int:id>', methods=['GET', 'POST'])
# def delete_category(id):
#     conn = get_db_connection()
#     category = conn.execute('SELECT * FROM categories WHERE id = ?', (id,)).fetchone()
#     if not category:
#         conn.close()
#         flash('Category not found.', 'danger')
#         return redirect(url_for('manage_categories'))

#     if category['name'] == 'Others':
#         flash('Cannot delete the "Others" category.', 'danger')
#         conn.close()
#         return redirect(url_for('manage_categories'))

#     if request.method == 'POST':
#         action = request.form.get('action')
#         if action == 'transfer':
#             # Transfer quotes to "Others"
#             conn.execute('UPDATE quotes SET category = ? WHERE category = ?', ('Others', category['name']))
#             # Delete the category
#             conn.execute('DELETE FROM categories WHERE id = ?', (id,))
#             conn.commit()
#             flash('Category deleted and quotes transferred to "Others".', 'success')
#         elif action == 'delete':
#             # Delete the quotes
#             conn.execute('DELETE FROM quotes WHERE category = ?', (category['name'],))
#             # Delete the category
#             conn.execute('DELETE FROM categories WHERE id = ?', (id,))
#             conn.commit()
#             flash('Category and associated quotes deleted.', 'success')
#         else:
#             flash('Invalid action.', 'danger')
#         conn.close()
#         return redirect(url_for('manage_categories'))

#     conn.close()
#     return render_template('delete_category.html', category=category)

# @app.template_global()
# def get_quote_count(category_name):
#     conn = get_db_connection()
#     count = conn.execute('SELECT COUNT(*) FROM quotes WHERE category = ?', (category_name,)).fetchone()[0]
#     conn.close()
#     return count

# if __name__ == '__main__':
#     init_db()
#     app.run(debug=True)