from app import app
from models import db, connect_db, User, Favorite, Game, Genre, Platform, Store, Developer, Publisher, Creator
import requests

api_key = '25160d19f0744f488c544b98e663fd62'

def get_raw_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


with app.app_context():
    db.drop_all()
    db.create_all()

    # games_data = get_raw_data(f'https://api.rawg.io/api/games?key={api_key}&search=The%20Witcher%203:%20Wild%20Hunt')

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

    # g1 = Game(
    #     name = games_data['results'][0]['name'],
    #     description = get_raw_data(f'https://api.rawg.io/api/games/{games_data["results"][0]["id"]}?key={api_key}')['description']
    
        
    # )




    db.session.add_all([u1, u2])
    db.session.commit()