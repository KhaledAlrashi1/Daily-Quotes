from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<Quote {self.id}>"