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
    favorite_id = db.Column(db.Integer, db.ForeignKey('favorites.id', ondelete='cascade'))
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'))


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password)
    """Sing up user. Hashes password adn adds user to system."""

    hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

    user = User(
        username=username,
        email=email,
        password=hashed_pwd
    )

    db.session.add(user)
    return user
    

    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', ondelete='cascade'))


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
    esrb_rating = db.Column(db.String, nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id', ondelete='cascade'))
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id', ondelete='cascade'))
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id', ondelete='cascade'))
    developer_id = db.Column(db.Integer, db.ForeignKey('developers.id', ondelete='cascade'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id', ondelete='cascade'))
    creator_id = db.Column(db.Integer, db.ForeignKey('creators.id', ondelete='cascade'))


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)


class Platform(db.Model):
    __tablename__ = 'platforms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    image_background = db.Column(db.Text)


class Store(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class Developer(db.Model):
    __tablename__ = 'developers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    games_count = db.Column(db.Integer)


class Publisher(db.Model):
    __tablename__ = 'publishers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    image_background = db.Column(db.Text)


class Creator(db.Model):
    __tablename__ = 'creators'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)


