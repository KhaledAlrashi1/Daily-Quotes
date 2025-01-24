# my_app/__init__.py
import secrets
from flask import Flask
from models import init_db

def create_app():
    app = Flask(__name__)
    
    # Set your secret key
    app.secret_key = secrets.token_hex(32)
    
    # Initialize the database (create tables if they don't exist)
    init_db()
    
    # Register your blueprints
    from routes.quotes import quotes_bp
    from routes.categories import categories_bp
    
    app.register_blueprint(quotes_bp)
    app.register_blueprint(categories_bp)
    
    # Example: a context processor for current_year if you like
    @app.context_processor
    def inject_current_year():
        from datetime import datetime
        return {'current_year': datetime.utcnow().year}
    
    return app