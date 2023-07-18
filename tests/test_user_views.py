"""User views tests"""

from unittest import TestCase
from models import db, connect_db, User
from forms import UserAddForm, UserEditForm, LoginForm
from app import app, CURR_USER_KEY
from sqlalchemy.exc import IntegrityError
from flask import request, session


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///videogame_library_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
# app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

class UserViewTestCase(TestCase):
    """Test views for users"""

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

        self.client = app.test_client()

    def tearDown(self):
        """tearDown is called after each test method is executed"""
        res = super().tearDown()
        db.session.rollback()
        return res

#############################################################################################################################
# Signup Tests

    def test_user_signup_valid(self):
        u2 = User.signup('testuser', 'testuser@email.com', 'testpassword')
        u2id = 222
        u2.id = u2id
        db.session.commit()

        self.assertIsNotNone(u2)
        self.assertEqual(u2.username, 'testuser')
        self.assertEqual(u2.email, 'testuser@email.com')
        self.assertIn('$2b', u2.password)
        with self.client as c:
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)       

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create Your Account', html)

    def test_user_signup_invalid_username(self):
        u3 = User.signup(None, 'testuser3@email.com', 'user3password')
        u3id = 333
        u3.id = u3id
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_user_signup_invalid_email(self):
        u4 = User.signup('testuser4', None, 'user4password')
        u4id = 444
        u4.id = u4id
        with self.assertRaises(IntegrityError) as context:
            db.session.commit()

    def test_user_signup_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            User.signup('testuser5', 'testuser5@email.com', None)

       
#############################################################################################################################
# Login Tests
        
    def test_user_login_valid(self):
        with self.client as c:
            # GET request to login page
            resp = c.get("/login")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log In', html)

            session[CURR_USER_KEY] = self.u1id
            self.assertIn(CURR_USER_KEY, session)

    def test_user_login_invalid(self):
        with self.client as c:
            # GET request to login page
            resp = c.get("/login")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log In', html)

            self.assertNotIn(CURR_USER_KEY, session)
    

#############################################################################################################################
# Logut Tests

    def test_user_logout(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1id
            del sess[CURR_USER_KEY]

            self.assertNotIn(CURR_USER_KEY, sess)

            resp = c.get('/logout', follow_redirects=True)
            self.assertNotIn('CURR_USER_KEY', sess)
            self.assertEqual(resp.status_code, 200)


 #############################################################################################################################
# Show user details Tests

    def test_user_details(self):
        with self.client as c:
            # Log in user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1id

            # GET request
            resp = c.get(f'/users/{self.u1id}')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'Your username: {self.u1.username}', html)

    
            

        

           

           


