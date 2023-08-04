"""Favorites views tests"""

from flask import Flask, redirect, request, render_template, session, flash, g, Blueprint
import requests
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Game, Category, GameCategory
from forms import UserAddForm, UserEditForm, LoginForm
from flask_bcrypt import Bcrypt
from my_secrets import MY_APP_API_KEY
from functions import add_game_to_db

from unittest import TestCase
from app import app, CURR_USER_KEY
from sqlalchemy.exc import IntegrityError
from datetime import date

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///videogame_library_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

db.drop_all()
db.create_all()


class FavoritesViewTestCase(TestCase):
    """Test views for favorites library"""

    def setUp(self):
        """Create test user and add sample data. setUp is called before each test method is executed."""

        db.drop_all()
        db.create_all()

        # Create user
        u1 = User.signup('sokka', 'sokka@email.com', 'password')
        u1id = 111
        u1.id = u1id

        db.session.commit()

        u1 = User.query.get(u1id)
 
        self.u1 = u1
        self.u1id = u1id

        # Add game to Game library
        g1 = Game(
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
        g1id = 123
        g1.id = g1id
        db.session.add(g1)
        db.session.commit()

        g1 = Game.query.get(g1id)
        self.g1 = g1
        self.g1id = g1id

        self.client = app.test_client()

    def tearDown(self):
        """tearDown is called after each test method is executed"""
        res = super().tearDown()
        db.session.rollback()
        return res


#############################################################################################################################

    def test_show_favorites(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1id
                self.assertIn(CURR_USER_KEY, sess)
                g.user = User.query.get(sess[CURR_USER_KEY])
                self.assertIsNotNone(g.user)
        
            resp = c.get(f"/users/{self.u1id}/favorites")
            html = resp.get_data(as_text=True)       

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<a class="nav-link active" aria-current="page" href="/users/111/favorites">Favorites</a>', html)


   
    def test_add_game_to_Game(self):
        g2 = Game(
            game_id = 4200,
            name = 'Portal 2',
            description = '<p>Portal 2 is a first-person puzzle game developed by Valve Corporation and released on April 19, 2011 on Steam, PS3 and Xbox 360. It was published by Valve Corporation in digital form and by Electronic Arts in physical form. </p><p>Its plot directly follows the first game&#39;s, taking place in the Half-Life universe. You play as Chell, a test subject in a research facility formerly ran by the company Aperture Science, but taken over by an evil AI that turned upon its creators, GladOS. After defeating GladOS at the end of the first game but failing to escape the facility, Chell is woken up from a stasis chamber by an AI personality core, Wheatley, as the unkempt complex is falling apart. As the two attempt to navigate through the ruins and escape, they stumble upon GladOS, and accidentally re-activate her...</p><p>Portal 2&#39;s core mechanics are very similar to the first game&#39;s ; the player must make their way through several test chambers which involve puzzles. For this purpose, they possess a Portal Gun, a weapon capable of creating teleportation portals on white surfaces. This seemingly simple mechanic and its subtleties coupled with the many different puzzle elements that can appear in puzzles allows the game to be easy to start playing, yet still feature profound gameplay. The sequel adds several new puzzle elements, such as gel that can render surfaces bouncy or allow you to accelerate when running on them.</p><p>The game is often praised for its gameplay, its memorable dialogue and writing and its aesthetic. Both games in the series are responsible for inspiring most puzzle games succeeding them, particularly first-person puzzle games. The series, its characters and even its items such as the portal gun and the companion cube have become a cultural icon within gaming communities.</p><p>Portal 2 also features a co-op mode where two players take on the roles of robots being led through tests by GladOS, as well as an in-depth level editor.</p>',
            released = date(2011, 4, 18),
            tba = False,
            background_image = 'https://media.rawg.io/media/games/328/3283617cb7d75d67257fc58339188742.jpg',
            game_series_count = 2,
            esrb_rating = 'Everyone 10+',
            genre =  '["Shooter", "Puzzle"]',
            platform = '["Xbox 360", "Linux", "macOS", "PlayStation 3", "PC", "Xbox One"]',
            store =  '["Xbox Store", "Steam", "PlayStation Store", "Xbox 360 Store"]',
            developer = 'Valve Software',
            publisher = '["Electronic Arts", "Valve"]'                           
        )
        g2id = 456
        g2.id = g2id
        db.session.add(g2)
        db.session.commit()

        g2 = Game.query.get(g2id)

        self.assertIsNotNone(g2)
        self.assertEqual(g2.game_id, 4200)
        self.assertEqual(g2.name, 'Portal 2')
        self.assertEqual(str(g2.released), '2011-04-18')
        self.assertEqual(g2.game_series_count, 2)
        self.assertEqual(g2.developer, 'Valve Software')


    def test_assign_game_to_favorites(self):
        cat1 = Category(
            favorites = self.g1.game_id,
            user_id = self.u1id
        )
        cat1id = 1
        cat1.id = cat1id
        db.session.add(cat1)
        db.session.commit()

        cat1 = Category.query.get(cat1id)

        self.assertIsNotNone(cat1)
        self.assertEqual(cat1.favorites, 3328)
        self.assertEqual(cat1.user_id, 111)

    def test_assign_game_to_game_category(self):
        cat1 = Category(
            favorites = self.g1.game_id,
            user_id = self.u1id
        )
        cat1id = 1
        cat1.id = cat1id
        db.session.add(cat1)
        db.session.commit()

        cat1 = Category.query.get(cat1id)
        g1 = Game.query.get(self.g1id)

        game_cat1 = GameCategory(
            game_id = g1.id,
            category_id = cat1.id
        )
        game_cat1id = 421
        game_cat1.id = game_cat1id
        db.session.add(game_cat1)
        db.session.commit()

        game_cat1 = GameCategory.query.get(game_cat1id)

        self.assertIsNotNone(game_cat1)
        self.assertEqual(game_cat1.game_id, 123)
        self.assertEqual(game_cat1.category_id, 1)


    def test_delete_game(self):
        cat1 = Category(
            favorites = self.g1.game_id,
            user_id = self.u1id
        )
        cat1id = 1
        cat1.id = cat1id
        db.session.add(cat1)
        db.session.commit()
        
        db.session.delete(cat1)
        db.session.commit()

        self.assertIsNone(Category.query.get(cat1id))
