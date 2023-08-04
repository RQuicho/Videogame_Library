from flask import Flask, redirect, request, render_template, session, flash, g, jsonify
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Game, Category, GameCategory
from forms import UserAddForm, UserEditForm, LoginForm
from flask_bcrypt import Bcrypt
from functions import add_game_to_db

# from my_secrets import MY_APP_API_KEY
import os
MY_APP_API_KEY = os.environ.get('MY_APP_API_KEY')

from admin.user import user
from all_games.all_games import all_games
from favorites.favorites import favorites
from played.played import played
from completed.completed import completed
from planned.planned import planned

app = Flask(__name__)

app.config.from_object("config")
connect_db(app)
# debug = DebugToolbarExtension(app)

bcrypt = Bcrypt()

CURR_USER_KEY = 'curr_user'


        

#############################################################################################################################
# Home Page


@app.route('/', methods=['GET', 'POST'])
def show_games():
    """Show all games from API"""

    search = request.args.get('q')
    
    if not search:
        response = requests.get(f'https://api.rawg.io/api/games?key={MY_APP_API_KEY}')
    else:
        response = requests.get(f'https://api.rawg.io/api/games?key={MY_APP_API_KEY}&search={search}')
    if response.status_code == 200:
        data = response.json()
        return render_template('show_entire_lib.html', response=data)
    else:
        return f'Error: Failed to retrieve data from the API. Response code: {response.status_code}. MY_APP_API_KEY: {MY_APP_API_KEY}'
        

@app.route('/platforms', methods=['GET', 'POST'])
def show_games_by_platform():
    """Show all games with platform filter"""

    search = request.args.get('q')
    platform_id = request.form.get('platform_id')
    # platform_id = request.form['platform_id']

    if platform_id:
        if search:
            response = requests.get(f'https://api.rawg.io/api/games?key={MY_APP_API_KEY}&parent_platforms={platform_id}&search={search}')
        else:
            response = requests.get(f'https://api.rawg.io/api/games?key={MY_APP_API_KEY}&parent_platforms={platform_id}')
    else:
        response = requests.get(f'https://api.rawg.io/api/games?key={MY_APP_API_KEY}&search={search}')

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
   
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={MY_APP_API_KEY}')
    
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


#############################################################################################################################
# API KEY route for scroll.js

@app.route('/get_api_key', methods=['GET'])
def get_api_key():
    return jsonify(api_key=MY_APP_API_KEY)





