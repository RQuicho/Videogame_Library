from app import app
from models import db, connect_db, User, Game, Category
import requests
from my_secrets import MY_APP_API_KEY


def get_raw_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


with app.app_context():
    db.drop_all()
    db.create_all()

    u1 = User.signup('Link', 'link@email.com', 'CookingIsFun')

    u2 = User.signup('Zelda', 'zelda@email.com', 'Thebloodmoonrises')

    db.session.add_all([u1, u2])
    db.session.commit()