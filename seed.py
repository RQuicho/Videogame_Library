from app import app
from models import db, connect_db, User, Game, Favorite, Played, Completed, Planned
import requests
from secrets import API_KEY


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

    u1 = User.signup('Link', 'link@email.com', 'CookingIsFun')

    u2 = User.signup('Zelda', 'zelda@email.com', 'The blood moon rises')

    # g1 = Game(
    #     name = games_data['results'][0]['name'],
    #     description = get_raw_data(f'https://api.rawg.io/api/games/{games_data["results"][0]["id"]}?key={api_key}')['description']
    
        
    # )




    db.session.add_all([u1, u2])
    db.session.commit()