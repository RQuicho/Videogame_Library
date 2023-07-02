from app import app
from models import db, connect_db, User, Favorite, Game, Genre, Platform, Store, Developer, Publisher, Creator

with app.app_context():
    db.drop_all()
    db.create_all()

    u1 = User(
        username='Link',
        password='CookingIsFun',
        email='link@email.com'
    )

    u2 = User(
        username='Zelda',
        password='The blood moon rises',
        email='zelda@email.com'
    )

    