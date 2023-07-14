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

@app.route('/users/<int:user_id>/completed', methods=['GET', 'POST'])
def show_user_completed(user_id):
    """Show user's completed library."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    if user_id != g.user.id:
        flash("Unauthorized user ID.", "danger")
        return redirect('/')
        
    user_id = g.user.id
    user = User.query.get_or_404(user_id)

    return render_template('/libraries/completed.html', user=user)


@app.route('/completed/<int:game_id>', methods=['POST'])
def add_completed(game_id):
    """Add game to Games table and add to correct Category"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    existing_category = Category.query.filter_by(completed=game_id, user_id=g.user.id).first()
    if existing_category:
        flash('Game already in Completed library', 'info')
        return redirect('/')

    add_game_to_db(game_id)
    
    # connect added game to correct user and Category table
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    if response.status_code == 200:
        # connect added game to Category table
        new_game = Game.query.filter_by(game_id=game_id).first()
        
        cat1 = Category(
            completed = new_game.game_id,
            user_id = g.user.id
        )
        db.session.add(cat1)
        db.session.commit()

        # connect added game to GameCategory table
        new_cat = Category.query.filter_by(completed=game_id).first()
        game_cat = GameCategory(
            game_id = new_game.id,
            category_id = new_cat.id
        )
        db.session.add(game_cat)
        db.session.commit()

        flash("Game added to Completed library", "success")
        return redirect('/')
    else:
        flash("Error: Fialed to retrieve game details from the API", "danger")
        return redirect('/')


@app.route('/delete_completed/<int:game_id>', methods=['POST'])
def delete_completed(game_id):
    """Delete game from completed library"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    category = Category.query.filter_by(completed=game_id, user_id=g.user.id).first()
    user_id = g.user.id
    db.session.delete(category)
    db.session.commit()
    flash("Game deleted from Completed library", "warning")

    return redirect(f'/users/{user_id}/completed')






#############################################################################################################################
# Planned routes

@app.route('/users/<int:user_id>/planned', methods=['GET', 'POST'])
def show_user_planned(user_id):
    """Show user's plan to play library."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    if user_id != g.user.id:
        flash("Unauthorized user ID.", "danger")
        return redirect('/')
        
    user_id = g.user.id
    user = User.query.get_or_404(user_id)

    return render_template('/libraries/planned.html', user=user)


@app.route('/planned/<int:game_id>', methods=['POST'])
def add_planned(game_id):
    """Add game to Games table and add to correct Category"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    existing_category = Category.query.filter_by(planned=game_id, user_id=g.user.id).first()
    if existing_category:
        flash('Game already in Plan To Play library', 'info')
        return redirect('/')

    add_game_to_db(game_id)
    
    # connect added game to correct user and Category table
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    if response.status_code == 200:
        # connect added game to Category table
        new_game = Game.query.filter_by(game_id=game_id).first()
        
        cat1 = Category(
            planned = new_game.game_id,
            user_id = g.user.id
        )
        db.session.add(cat1)
        db.session.commit()

        # connect added game to GameCategory table
        new_cat = Category.query.filter_by(planned=game_id).first()
        game_cat = GameCategory(
            game_id = new_game.id,
            category_id = new_cat.id
        )
        db.session.add(game_cat)
        db.session.commit()

        flash("Game added to Plan to Play library", "success")
        return redirect('/')
    else:
        flash("Error: Fialed to retrieve game details from the API", "danger")
        return redirect('/')


@app.route('/delete_planned/<int:game_id>', methods=['POST'])
def delete_planned(game_id):
    """Delete game from planned library"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    category = Category.query.filter_by(planned=game_id, user_id=g.user.id).first()
    user_id = g.user.id
    db.session.delete(category)
    db.session.commit()
    flash("Game deleted from Plan To Play library", "warning")

    return redirect(f'/users/{user_id}/planned')





