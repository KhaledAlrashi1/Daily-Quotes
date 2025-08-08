# Daily Quotes

A simple Flask-based web application for displaying, adding, and organizing inspirational quotes. It features daily quote rotation, category management, and a clean Bootstrap‑powered interface.

---

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Important Concepts](#important-concepts)
- [Next Steps](#next-steps)

---

## Features
- **Daily Quote Rotation** – Shows a new quote for each category every day for continual variety.  
- **Category Management** – Full CRUD support for categories, including manual ordering and safe handling of associated quotes.  
- **Quote Management** – Add, edit, delete, search, and get live suggestions for quotes.  
- **Paginated “All Quotes” View** – Displays every quote with a *persistent* shuffle stored in the user session.  
- **Responsive UI** – Built with Bootstrap, complemented by custom CSS animations and a hero section.  
- **JSON Endpoint** – Exposes quote‑count data for front‑end widgets or external integrations.

---

## Project Structure

| Path / Module | Description |
|---------------|-------------|
| `run.py` | Entry point; launches the Flask app on port **5010** in debug mode. |
| `__init__.py` | Application factory; sets up Flask, secret key, database tables, and blueprints. |
| `models.py` | SQLite helpers; opens connections and initializes `quotes` & `categories` tables. |
| `utils.py` | Manages `quote_offset.json` to rotate quotes daily. |
| `routes/` | Package holding Flask blueprints. |
| `routes/quotes.py` | Home page, quote CRUD, search, “All Quotes” view, quote‑count JSON. |
| `routes/categories.py` | Category CRUD, ordering, quote transfer/deletion. |
| `templates/` | Jinja2 templates; `base.html` defines layout and shared UI. |
| `static/` | `styles.css`, images, and other static assets. |

---

## Important Concepts
- **Flask Blueprints** – Separate modules (`quotes_bp`, `categories_bp`) keep related routes organized.  
- **Application Factory Pattern** – `create_app()` in `__init__.py` assembles the app, DB, and blueprints.  
- **SQLite Integration** – Uses `sqlite3` with a *Row factory* for dict‑like access to columns.  
- **Session‑Based Randomization** – The “All Quotes” view stores a shuffled quote list in the session, keeping pagination consistent.  
- **Daily Quote Rotation** – `quote_offset.json` tracks per‑category offsets so each day surfaces the next quote.

---

## Next Steps
1. **Flask Fundamentals** – Deep‑dive into blueprints, context processors, and app factories.  
2. **Jinja2 Mastery** – Leverage template inheritance, macros, and global functions.  
3. **SQLite & SQL** – Learn schema design, write direct queries, and explore migration tools.  
4. **Frontend Polish** – Customize Bootstrap, refine CSS animations, and enhance UX with JavaScript (e.g., Fetch API).  
5. **Testing & Deployment** – Add unit tests with *pytest* and experiment with Docker, uWSGI, or cloud platforms for production deployment.
