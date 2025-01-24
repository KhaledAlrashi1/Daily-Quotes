# my_app/routes/categories.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3
from models import get_db_connection
from routes.quotes import get_quote_count

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET', 'POST'])
def manage_categories():
    conn = get_db_connection()
    if request.method == 'POST':
        if 'update_order' in request.form:
            # Updating the order
            orders = request.form.getlist('order')
            ids = request.form.getlist('id')
            for category_id, order_val in zip(ids, orders):
                conn.execute('UPDATE categories SET "order" = ? WHERE id = ?', (int(order_val), int(category_id)))
            conn.commit()
            flash('Category order updated successfully!', 'success')
            conn.close()
            return redirect(url_for('categories.manage_categories'))
        elif 'add_category' in request.form:
            # Adding a new category
            category_name = request.form.get('category_name', '').strip()
            quote_text = request.form.get('quote_text', '').strip()
            if category_name and quote_text:
                try:
                    max_order = conn.execute('SELECT MAX("order") FROM categories').fetchone()[0]
                    if max_order is None:
                        max_order = 0
                    next_order = max_order + 1
                    conn.execute('INSERT INTO categories (name, "order") VALUES (?, ?)', (category_name, next_order))
                    conn.execute('INSERT INTO quotes (text, category) VALUES (?, ?)', (quote_text, category_name))
                    conn.commit()
                    flash('Category and quote added successfully!', 'success')
                except sqlite3.IntegrityError:
                    flash('Category already exists.', 'danger')
                conn.close()
                return redirect(url_for('categories.manage_categories'))
            else:
                flash('Please enter both a category name and an initial quote.', 'danger')
                conn.close()
                return redirect(url_for('categories.manage_categories'))
    else:
        # Display categories
        categories = conn.execute('SELECT * FROM categories ORDER BY "order" ASC').fetchall()
        conn.close()
        return render_template('categories.html', categories=categories)

@categories_bp.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM categories WHERE id = ?', (id,)).fetchone()
    if not category:
        conn.close()
        flash('Category not found.', 'danger')
        return redirect(url_for('categories.manage_categories'))

    if request.method == 'POST':
        new_name = request.form.get('category_name', '').strip()
        if new_name:
            try:
                # Update categories table
                conn.execute('UPDATE categories SET name = ? WHERE id = ?', (new_name, id))
                # Update quotes table
                conn.execute('UPDATE quotes SET category = ? WHERE category = ?', (new_name, category['name']))
                conn.commit()
                flash('Category updated successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('Category name already exists.', 'danger')
            conn.close()
            return redirect(url_for('categories.manage_categories'))
        else:
            flash('Please enter a category name.', 'danger')
    conn.close()
    return render_template('edit_category.html', category=category)


@categories_bp.route('/delete_category/<int:id>', methods=['GET', 'POST'])
def delete_category(id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM categories WHERE id = ?', (id,)).fetchone()
    if not category:
        conn.close()
        flash('Category not found.', 'danger')
        return redirect(url_for('categories.manage_categories'))

    if category['name'] == 'Others':
        flash('Cannot delete the "Others" category.', 'danger')
        conn.close()
        return redirect(url_for('categories.manage_categories'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'transfer':
            # Transfer quotes
            conn.execute('UPDATE quotes SET category = ? WHERE category = ?', ('Others', category['name']))
            conn.execute('DELETE FROM categories WHERE id = ?', (id,))
            conn.commit()
            flash('Category deleted and quotes transferred to "Others".', 'success')
        elif action == 'delete':
            # Delete quotes
            conn.execute('DELETE FROM quotes WHERE category = ?', (category['name'],))
            conn.execute('DELETE FROM categories WHERE id = ?', (id,))
            conn.commit()
            flash('Category and associated quotes deleted.', 'success')
        else:
            flash('Invalid action.', 'danger')
        conn.close()
        return redirect(url_for('categories.manage_categories'))

    conn.close()
    return render_template('delete_category.html', category=category)