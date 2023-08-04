from flask import Flask, redirect, request, render_template, session, flash, g
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Game, Category, GameCategory
from forms import UserAddForm, UserEditForm, LoginForm
from flask_bcrypt import Bcrypt
import os
MY_APP_API_KEY = os.environ.get('MY_APP_API_KEY')

def add_game_to_db(game_id):
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={MY_APP_API_KEY}') 
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