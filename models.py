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
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    # possibly add a user image later

    # game = db.relationship('Game', backref='users')

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
            return False


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    released = db.Column(db.Date)
    tba = db.Column(db.Boolean)
    background_image = db.Column(db.Text)
    rating = db.Column(db.Integer)
    game_series_count = db.Column(db.Integer)
    esrb_rating = db.Column(db.String)
    genre = db.Column(db.Text)
    platform = db.Column(db.Text)
    store = db.Column(db.Text)
    developer = db.Column(db.Text)
    publisher = db.Column(db.Text)
    creator = db.Column(db.Text)
    favorite_id = db.Column(db.Integer, db.ForeignKey('favorites.id', ondelete='cascade'))
    played_id = db.Column(db.Integer, db.ForeignKey('played.id', ondelete='cascade'))
    completed_id = db.Column(db.Integer, db.ForeignKey('completed.id', ondelete='cascade'))
    planned_id = db.Column(db.Integer, db.ForeignKey('planned.id', ondelete='cascade'))


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    genre = db.Column(db.String)
    platform = db.Column(db.String)
    released = db.Column(db.String)
    esrb_rating = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'))

    # game = db.relationship('Game', backref='favorites')


class Played(db.Model):
    __tablename__ = 'played'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    genre = db.Column(db.String)
    platform = db.Column(db.String)
    released = db.Column(db.String)
    esrb_rating = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'))

    # game = db.relationship('Game', backref='played')


class Completed(db.Model):
    __tablename__ = 'completed'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    genre = db.Column(db.String)
    platform = db.Column(db.String)
    released = db.Column(db.String)
    esrb_rating = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'))

    # game = db.relationship('Game', backref='completed')


class Planned(db.Model):
    __tablename__ = 'planned'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    genre = db.Column(db.String)
    platform = db.Column(db.String)
    released = db.Column(db.String)
    esrb_rating = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'))

    # game = db.relationship('Game', backref='planned')


