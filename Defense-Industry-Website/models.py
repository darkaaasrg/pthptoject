from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship # Не використовується, але гарно мати для майбутнього

db = SQLAlchemy()

# -------------------- Користувач (адмін) -------------------- #
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    def check_password(self, password):
        return self.password == password


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    img = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Product {self.name}>"

class CarouselItem(db.Model):
    __tablename__ = "carousel_items"

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    text_position = db.Column(db.String(20), default="center")
    button_text = db.Column(db.String(100), default="")
    button_link = db.Column(db.String(200), default="#")

    def __repr__(self):
        return f"<CarouselItem {self.title}>"
