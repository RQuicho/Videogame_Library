from flask import Flask, redirect, request, render_template, session, flash, g
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Game, Category, GameCategory
from forms import UserAddForm, UserEditForm, LoginForm
from flask_bcrypt import Bcrypt
from secrets import API_KEY

from admin.player import player
from all_games.all_games import all_games

app = Flask(__name__)

app.config.from_object("config")
connect_db(app)
debug = DebugToolbarExtension(app)

bcrypt = Bcrypt()

CURR_USER_KEY = 'curr_user'

def add_game_to_db(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}') 
    if response.status_code == 200:
        game = response.json()
        # game_id = game.id
        g1 = Game(
            game_id = game['id'],
            name = game['name'],
            description = game['description'],
            released = game['released'],
            tba = game['tba'],
            background_image = game['background_image'],
            game_series_count = game['game_series_count'],
            esrb_rating = game['esrb_rating']['name'] if game['esrb_rating'] else 'N/A',
            genre = [genre['name'] for genre in game['genres']] if game['genres'] else 'N/A',
            platform = [platform['platform']['name'] for platform in game['platforms']],
            store = [store['store']['name'] for store in game['stores']],
            developer = game['developers'][0]['name'],
            publisher = game['publishers'][0]['name'] if game['publishers'] else 'N/A'
                           
        )
    db.session.add(g1)
    db.session.commit()
        

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


app.register_blueprint(player, url_prefix="")


    
#############################################################################################################################
# All_Games routes


app.register_blueprint(all_games, url_prefix="")


#############################################################################################################################
# Favorites routes

@app.route('/users/<int:user_id>/favorites', methods=['GET', 'POST'])
def show_user_favorites(user_id):
    """Show user's favorites library."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    if user_id != g.user.id:
        flash("Unauthorized user ID.", "danger")
        return redirect('/')
        
    user_id = g.user.id
    user = User.query.get_or_404(user_id)

    return render_template('/libraries/favorites.html', user=user)


@app.route('/favorites/<int:game_id>', methods=['POST'])
def add_favorite(game_id):
    """Add game to Games table and add to correct Category"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    existing_category = Category.query.filter_by(favorites=game_id, user_id=g.user.id).first()
    if existing_category:
        flash('Game already in Favorites library', 'info')
        return redirect('/')

    add_game_to_db(game_id)
    
    # connect added game to correct user and Category table
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    if response.status_code == 200:
        # connect added game to Category table
        new_game = Game.query.filter_by(game_id=game_id).first()
        
        cat1 = Category(
            favorites = new_game.game_id,
            user_id = g.user.id
        )
        db.session.add(cat1)
        db.session.commit()

        # connect added game to GameCategory table
        new_cat = Category.query.filter_by(favorites=game_id).first()
        game_cat = GameCategory(
            game_id = new_game.id,
            category_id = new_cat.id
        )
        db.session.add(game_cat)
        db.session.commit()

        flash("Game added to Favorites library", "success")
        return redirect('/')
    else:
        flash("Error: Fialed to retrieve game details from the API", "danger")
        return redirect('/')


@app.route('/delete_favorite/<int:game_id>', methods=['POST'])
def delete_favorite(game_id):
    """Delete game from favorites library"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    category = Category.query.filter_by(favorites=game_id, user_id=g.user.id).first()
    user_id = g.user.id
    db.session.delete(category)
    db.session.commit()
    flash("Game deleted from Favorites library", "warning")

    return redirect(f'/users/{user_id}/favorites')




#############################################################################################################################
# Played routes

@app.route('/users/<int:user_id>/played', methods=['GET', 'POST'])
def show_user_played(user_id):
    """Show user's played library."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    if user_id != g.user.id:
        flash("Unauthorized user ID.", "danger")
        return redirect('/')
        
    user_id = g.user.id
    user = User.query.get_or_404(user_id)

    return render_template('/libraries/played.html', user=user)


@app.route('/played/<int:game_id>', methods=['POST'])
def add_played(game_id):
    """Add game to Games table and add to correct Category"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    existing_category = Category.query.filter_by(played=game_id, user_id=g.user.id).first()
    if existing_category:
        flash('Game already in Played library', 'info')
        return redirect('/')

    add_game_to_db(game_id)
    
    # connect added game to correct user and Category table
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
    if response.status_code == 200:
        # connect added game to Category table
        new_game = Game.query.filter_by(game_id=game_id).first()
        
        cat1 = Category(
            played = new_game.game_id,
            user_id = g.user.id
        )
        db.session.add(cat1)
        db.session.commit()

        # connect added game to GameCategory table
        new_cat = Category.query.filter_by(played=game_id).first()
        game_cat = GameCategory(
            game_id = new_game.id,
            category_id = new_cat.id
        )
        db.session.add(game_cat)
        db.session.commit()

        flash("Game added to Played library", "success")
        return redirect('/')
    else:
        flash("Error: Fialed to retrieve game details from the API", "danger")
        return redirect('/')


@app.route('/delete_played/<int:game_id>', methods=['POST'])
def delete_played(game_id):
    """Delete game from played library"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    category = Category.query.filter_by(played=game_id, user_id=g.user.id).first()
    user_id = g.user.id
    db.session.delete(category)
    db.session.commit()
    flash("Game deleted from Played library", "warning")

    return redirect(f'/users/{user_id}/played')




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





