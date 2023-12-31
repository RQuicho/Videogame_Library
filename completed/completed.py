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

completed = Blueprint("completed", __name__, template_folder="templates")

@completed.route('/users/<int:user_id>/completed', methods=['GET', 'POST'])
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

    return render_template('completed.html', user=user)


@completed.route('/completed/<int:game_id>', methods=['POST'])
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
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={MY_APP_API_KEY}')
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


@completed.route('/delete_completed/<int:game_id>', methods=['POST'])
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