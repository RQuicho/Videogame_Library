from flask import Flask, redirect, request, render_template, session, flash, g, Blueprint
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Game, Category, GameCategory
from forms import UserAddForm, UserEditForm, LoginForm
from flask_bcrypt import Bcrypt
import os
MY_APP_API_KEY = os.environ.get('MY_APP_API_KEY')

user = Blueprint("user", __name__, template_folder="templates")
bcrypt = Bcrypt()

CURR_USER_KEY = 'curr_user'


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@user.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sing up new user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(form.username.data, form.email.data, form.password.data)
            db.session.commit()
            flash(f"Welcome {user.username}!", "success")
            do_login(user)
            return redirect("/")
        except IntegrityError:
            flash("Usrename already taken", "danger")
            return render_template('signup.html', form=form)
    else:
        return render_template('signup.html', form=form)


@user.route('/login', methods=['GET', 'POST'])
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


@user.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout user."""

    do_logout()
    flash("Successfully logged out!", "success")
    return redirect("/")


@user.route('/users/<int:user_id>', methods=['GET', 'POST'])
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
        user.username = form.username.data
        user.email = form.email.data
        
        if form.password.data:
            hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
            if form.password.data == form.confirm_password.data:
                user.password = hashed_pwd
            else:
                flash("Passwords do not match", "danger")
                return render_template('user_details.html', user=user, form=form)

        db.session.commit()
        flash("Successfully updated profile!", "success")
        return redirect('/')

    return render_template('user_details.html', user=user, form=form)
