from flask import Flask, redirect, request, render_template, session, flash, g, Blueprint
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Game, Category, GameCategory
from forms import UserAddForm, UserEditForm, LoginForm
from flask_bcrypt import Bcrypt
import os
MY_APP_API_KEY = os.environ.get('MY_APP_API_KEY')
from functions import add_game_to_db


all_games = Blueprint("all_games", __name__, template_folder="templates")


@all_games.route('/users/<int:user_id>/all_games', methods=['GET', 'POST'])
def show_user_all_games(user_id):
    """Show user's all_games library."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    if user_id != g.user.id:
        flash("Unauthorized user ID.", "danger")
        return redirect('/')
        
    user_id = g.user.id
    user = User.query.get_or_404(user_id)

    return render_template('all_games.html', user=user)


@all_games.route('/all_games/<int:game_id>', methods=['POST'])
def add_all_game(game_id):
    """Add game to Games table and add to correct Category"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    existing_category = Category.query.filter_by(all_games=game_id, user_id=g.user.id).first()
    if existing_category:
        flash('Game already in All Games library', 'info')
        return redirect('/')

    add_game_to_db(game_id)
    
    # connect added game to correct user and Category table
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={MY_APP_API_KEY}')
    if response.status_code == 200:
        # connect added game to Category table
        new_game = Game.query.filter_by(game_id=game_id).first()
        
        cat1 = Category(
            all_games = new_game.game_id,
            user_id = g.user.id
        )
        db.session.add(cat1)
        db.session.commit()

        # connect added game to GameCategory table
        new_cat = Category.query.filter_by(all_games=game_id).first()
        game_cat = GameCategory(
            game_id = new_game.id,
            category_id = new_cat.id
        )
        db.session.add(game_cat)
        db.session.commit()

        flash("Game added to All Games library", "success")
        return redirect('/')
    else:
        flash("Error: Fialed to retrieve game details from the API", "danger")
        return redirect('/')


@all_games.route('/delete_all_game/<int:game_id>', methods=['POST'])
def delete_all_game(game_id):
    """Delete game from all_games library"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    category = Category.query.filter_by(all_games=game_id, user_id=g.user.id).first()
    user_id = g.user.id
    db.session.delete(category)
    db.session.commit()
    flash("Game deleted from All Games library", "warning")

    return redirect(f'/users/{user_id}/all_games')