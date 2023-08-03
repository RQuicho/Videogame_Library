from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'))

    categories = db.relationship('Category', backref='users')


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, pwd):
        """Sign up user. Hashes password adn adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(pwd).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists and password is correct."""

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return None


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False, default='N/A')
    released = db.Column(db.Date, default='N/A')
    tba = db.Column(db.Boolean, default='N/A')
    background_image = db.Column(db.Text, default='N/A')
    game_series_count = db.Column(db.Integer, default='N/A')
    esrb_rating = db.Column(db.String, default='N/A')
    genre = db.Column(db.JSON, default='N/A')
    platform = db.Column(db.JSON, default='N/A')
    store = db.Column(db.JSON, default='N/A')
    developer = db.Column(db.JSON, default='N/A')
    publisher = db.Column(db.JSON, default='N/A')

    users = db.relationship('User', backref='games')

    def __repr__(self):
        return f"<Game #{self.id}:, game_id: {self.game_id}, name: {self.name}>"
    


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    all_games = db.Column(db.Integer)
    favorites = db.Column(db.Integer)
    played = db.Column(db.Integer)
    completed = db.Column(db.Integer)
    planned = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    games = db.relationship('Game', secondary='games_categories', backref='categories')

    def __repr__(self):
        return f"<Category #{self.id}, all_games: {self.all_games}, favorites: {self.favorites}, played: {self.played}, completed: {self.completed}, planned: {self.planned}, user_id: {self.user_id}>"


class GameCategory(db.Model):
    __tablename__ = 'games_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)