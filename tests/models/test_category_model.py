"""Category model tests"""

from unittest import TestCase
from models import db, User, Game, Category
from app import app
from sqlalchemy.exc import IntegrityError
from datetime import date

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///videogame_library_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

db.drop_all()
db.create_all()

class CategoryModelTestCase(TestCase):
    """Test views for Category model"""

    def setUp(self):
        """Create test user and add sample data. setUp is called before each test method is executed."""

        db.drop_all()
        db.create_all()

        u1 = User.signup('sokka', 'sokka@email.com', 'password')
        u1id = 111
        u1.id = u1id

        db.session.commit()

        u1 = User.query.get(u1id)

        self.u1 = u1
        self.u1id = u1id

        

        g = Game(
            game_id = 3328,
            name = 'The Witcher 3: Wild Hunt',
            description = '<p>The third game in a series, it holds nothing back from the player. Open world adventures of the renowned monster slayer Geralt of Rivia are now even on a larger scale. Following the source material more accurately, this time Geralt is trying to find the child of the prophecy, Ciri while making a quick coin from various contracts on the side. Great attention to the world building above all creates an immersive story, where your decisions will shape the world around you.</p><p>CD Project Red are infamous for the amount of work they put into their games, and it shows, because aside from classic third-person action RPG base game they provided 2 massive DLCs with unique questlines and 16 smaller DLCs, containing extra quests and items.</p><p>Players praise the game for its atmosphere and a wide open world that finds the balance between fantasy elements and realistic and believable mechanics, and the game deserved numerous awards for every aspect of the game, from music to direction.</p>',
            released = date(2015, 5, 18),
            tba = False,
            background_image = 'https://media.rawg.io/media/games/618/618c2031a07bbff6b4f611f10b6bcdbc.jpg',
            game_series_count = 8,
            esrb_rating = 'Mature',
            genre =  '["Action", "Adventure", "RPG"]',
            platform = '["Xbox Series S/X", "PlayStation 4", "Nintendo Switch", "PC", "Xbox One", "PlayStation 5"]',
            store =  '["GOG", "PlayStation Store", "Steam", "Xbox Store", "Nintendo Store"]',
            developer = 'CD PROJEKT RED',
            publisher = 'CD PROJEKT RED'                           
        )
        gid = 1
        db.session.add(g)
        db.session.commit()

        g = Game.query.get(gid)
        self.g = g
        self.gid = gid
        self.g.game_id = g.game_id

        self.client = app.test_client()

    def tearDown(self):
        """tearDown is called after each test method is executed"""
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_category_model(self):
        """Tests basic category model"""

        c = Category(
            all_games = self.g.game_id,
            user_id = self.u1id
        )
        cid = 1
        db.session.add(c)
        db.session.commit()

        c = Category.query.get(cid)
        self.c = c
        self.cid = cid
        self.c.all_games = c.all_games
        self.c.user_id = c.user_id

        self.assertEqual(self.c.all_games, 3328)
        self.assertEqual(self.cid, 1)
        self.assertEqual(self.c.user_id, 111)