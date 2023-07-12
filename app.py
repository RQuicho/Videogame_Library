from flask import Flask, redirect, request, render_template, session, flash, g
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Game, Category, GameCategory
from forms import UserAddForm, UserEditForm, LoginForm
from flask_bcrypt import Bcrypt
from secrets import API_KEY

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
    """Show all games"""

    search = request.args.get('q')
    # possibly include a random page at end of url to randomly show games 
    # https://api.rawg.io/api/games?key=25160d19f0744f488c544b98e663fd62&page=2

    if not search:
        response = requests.get(f'https://api.rawg.io/api/games?key={API_KEY}')
    else:
        response = requests.get(f'https://api.rawg.io/api/games?key={API_KEY}&search={search}')
    if response.status_code == 200:
        data = response.json()
        return render_template('show_all_games.html', response=data)
    else:
        return "Error: Failed to retrieve data from the API"

       

    # 'next': 'https://api.rawg.io/api/games?key=25160d19f0744f488c544b98e663fd62&page=2', 'previous': None

    # https://api.rawg.io/api/games?key=25160d19f0744f488c544b98e663fd62

    # https://api.rawg.io/api/games?key=25160d19f0744f488c544b98e663fd62&search=witcher

    # https://api.rawg.io/api/games/{id} (.description)



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
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If user is logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sing up new user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.commit()
        except IntegrityError:
            flash("Usrename already taken", "danger")
            return render_template('signup.html', form=form)

        do_login(user)
        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login user."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            flash(f"Hello {user.username}!", "success")
            return redirect("/")
        flash("Invalid credentials.", "danger")
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout user."""

    do_logout()
    flash("Successfully logged out!", "success")
    return redirect("/")



#############################################################################################################################
# User routes

@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def show_user_details(user_id):
    """Show user details and update info."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    if user_id != g.user.id:
        flash("Unauthorized user ID.", "danger")
        return redirect('/')

    user_id = g.user.id
    user = User.query.get_or_404(user_id)

    form = UserEditForm(obj=user)
    if form.validate_on_submit():
        if form.password.data:
            if User.authenticate(form.username.data, form.password.data):
                user.username = form.username.data
                user.email = form.email.data
                user.password = hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
                db.session.commit()
                flash("Successfully updated profile!", "success")
            else:
                flash("Password Incorrect", "danger")
        else:
            user.username = form.username.data
            user.email = form.email.data
            db.session.commit()
            flash("Successfully updated profile!", "success")
        return redirect('/')
    return render_template('user_details.html', user=user, form=form)


    
#############################################################################################################################
# All_Games routes

@app.route('/users/<int:user_id>/all_games', methods=['GET', 'POST'])
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

    return render_template('user_all_games.html', user=user)


@app.route('/all_games/<int:game_id>', methods=['POST'])
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
    response = requests.get(f'https://api.rawg.io/api/games/{game_id}?key={API_KEY}')
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


@app.route('/delete_game/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    """Delete game from all_games library"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    game = Game.query.filter_by(game_id=game_id).first()
    user_id = g.user.id
    category = Category.query.filter_by(all_games=game_id).first()

    db.session.delete(game)
    db.session.delete(category)
    db.session.commit()

    return redirect(f'/users/{user_id}/all_games')



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

    return render_template('user_favorites.html', user=user)


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

    






#############################################################################################################################
# Played routes








#############################################################################################################################
# Completed routes








#############################################################################################################################
# Planned routes







