"""User model tests"""

from unittest import TestCase
from models import db, User
from app import app
from sqlalchemy.exc import IntegrityError

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///videogame_library_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test views for User model"""

    def setUp(self):
        """Create test user and add sample data. setUp is called before each test method is executed."""

        db.drop_all()
        db.create_all()

        u1 = User.signup('sokka', 'sokka@email.com', 'password')
        u1id = 111
        u1.id = u1id

        u2 = User.signup('katara', 'katara@email.com', 'password2')
        u2id = 222
        u2.id = u2id

        db.session.commit()

        u1 = User.query.get(u1id)
        u2 = User.query.get(u2id)

        self.u1 = u1
        self.u1id = u1id
        self.u2 = u2
        self.u2id = u2id

        self.client = app.test_client()

    def tearDown(self):
        """tearDown is called after each test method is executed"""
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Tests basic user model"""

        u = User(
            username="toph",
            password="melonlord",
            email="toph@email.com"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(u.game_id, None)


    def test_valid_signup(self):
        u3 = User.signup('aang', 'aang@email.com', 'password3')
        u3id = 333
        u3.id = u3id
        db.session.commit()

        u3 = User.query.get(u3id)

        self.assertIsNotNone(u3)
        self.assertEqual(u3.username, 'aang')
        self.assertIn('$2b', u3.password)
        self.assertEqual(u3.email, 'aang@email.com')

    def test_invalid_username_signup(self):
        u4 = User.signup(None, 'invalid@email.com', 'password4')
        u4id = 444
        u4.id = u4id
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_email_signup(self):
        u4 = User.signup('testuser', None, 'password4')
        u4id = 444
        u4.id = u4id
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup('testuser', 'test@email.com', None)

    def test_valid_auth(self):
        self.assertTrue(User.authenticate(self.u1.username, 'password'))

    def test_invalid_username(self):
        self.assertFalse(User.authenticate('wrong', 'password'))

    def test_invalid_password(self):
        self.assertFalse(User.authenticate('sokka', 'wrong'))

    

    
