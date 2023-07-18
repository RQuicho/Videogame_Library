from flask import Flask, redirect, request, render_template, session, flash, g
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Game, Category, GameCategory
from forms import UserAddForm, UserEditForm, LoginForm
from flask_bcrypt import Bcrypt
from secrets import API_KEY
from functions import add_game_to_db

from admin.user import user
from all_games.all_games import all_games
from favorites.favorites import favorites
from played.played import played
from completed.completed import completed
from planned.planned import planned

app = Flask(__name__)

app.config.from_object("config")
connect_db(app)
debug = DebugToolbarExtension(app)

bcrypt = Bcrypt()

CURR_USER_KEY = 'curr_user'


        

#############################################################################################################################
# Home Page


@app.route('/', methods=['GET', 'POST'])
def show_games():
    """Show all games from API"""

    search = request.args.get('q')
    # possibly include a random page at end of url to randomly show games 
    # or implement continuous scroll function using JavaScript
    # https://api.rawg.io/api/games?key=25160d19f0744f488c544b98e663fd62&page=2

    if not search:
        response = requests.get(f'https://api.rawg.io/api/games?key={API_KEY}')
    else:
        response = requests.get(f'https://api.rawg.io/api/games?key={API_KEY}&search={search}')
    if response.status_code == 200:
        data = response.json()
        return render_template('show_entire_lib.html', response=data)
    else:
        return "Error: Failed to retrieve data from the API"


#############################################################################################################################
# Game Details routes

@app.route('/games/<int:game_id>', methods=['GET'])
def show_game_details(game_id):
    """Shows detail of one game"""
   
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    
    if response.status_code == 200:
        data = response.json()
        return render_template('game_details.html', game=data)
    else:
        return "Error: Failed to retrieve data from the API"


#############################################################################################################################
# User routes

@app.before_request
def add_user_to_g():
    """If user is logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


app.register_blueprint(user, url_prefix="")


    
#############################################################################################################################
# All_Games routes


app.register_blueprint(all_games, url_prefix="")


#############################################################################################################################
# Favorites routes

app.register_blueprint(favorites, url_prefix="")



#############################################################################################################################
# Played routes

app.register_blueprint(played, url_prefix="")



#############################################################################################################################
# Completed routes

app.register_blueprint(completed, url_prefix="")



#############################################################################################################################
# Planned routes

app.register_blueprint(planned, url_prefix="")





