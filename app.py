from flask import Flask, redirect, request, render_template, session, flash, g
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Favorite, Game, Genre, Platform, Store, Developer, Publisher, Creator
from forms import UserForm, LoginForm

app = Flask(__name__)

app.config.from_object("config")
connect_db(app)
debug = DebugToolbarExtension(app)

CURR_USER_KEY = 'curr_user'

api_key = '25160d19f0744f488c544b98e663fd62'

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
    form = UserForm()

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
    return redirect("/login")

    
#############################################################################################################################
# User routes




@app.route('/', methods=['GET'])
def show_games():
    """Show all games"""

    response = requests.get(f'https://api.rawg.io/api/games?key={api_key}')
    # response2 = requests.get(f'https://api.rawg.io/api/games?key={api_key}&page=2')

    if response.status_code == 200:
        data = response.json()
        # data2 = response2.json()
        return render_template('show_all_games.html', response=data)
    else:
        return "Error: Failed to retrieve data from the API"

    # 'next': 'https://api.rawg.io/api/games?key=25160d19f0744f488c544b98e663fd62&page=2', 'previous': None

    # https://api.rawg.io/api/games?key=25160d19f0744f488c544b98e663fd62

    

# response = requests.get(f'https://api.exchangerate.host/convert?from={first_curr}&to={second_curr}&amount={amount}&places=2')
# https://api.rawg.io/api/creators/{id}
# https://api.rawg.io/api/creators

