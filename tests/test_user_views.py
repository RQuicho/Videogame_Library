"""User views tests"""

from unittest import TestCase
from models import db, connect_db, User
from forms import UserAddForm, UserEditForm, LoginForm
from app import app, CURR_USER_KEY
from sqlalchemy.exc import IntegrityError
from flask import request


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

    def test_user_signup(self):  
        with self.client as c:
            # GET request
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)       

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Create Your Account', html)

            # POST request
            resp = c.post("/signup", data={
                "username": "testuser",
                "email": "testuser@email.com",
                "password": "testpassword"
            }, follow_redirects=True)
                
            self.assertEqual(resp.status_code, 200)

        
    def test_user_login(self):
        with self.client as c:
            # GET request to login page
            resp = c.get("/login")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log In', html)

            # POST request with valid login credentials
            resp = c.post("/login", data={
                "username": "sokka",
                "password": "password"
            }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # self.assertIn('Hello sokka!', html)
    

    def test_user_logout(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1id
            
            resp = c.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertNotIn('CURR_USER_KEY', sess)
            self.assertEqual(resp.status_code, 200)
            # self.assertIn('Successfully logged out!', html)


    def test_user_details(self):
        with self.client as c:
            # Log in user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1id

            # GET request
            resp = c.get(f'/users/{self.u1id}')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Your username:', html)

    def test_user_details_edit_success(self):
        with self.client as c:
            # Log in user
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1id

            # POST request to update user info
            resp = c.post(f'/users/{self.u1id}', data={
                'username': 'sokkanew',
                'email': 'sokkanew@email.com',
                'password': 'newpassword',
                'confirm_password': 'newpassword'
            }, follow_redirects=True)
           
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            # self.assertIn('Successfully updated profile!', html)

            # Check is user details were updated
            updated_user = User.query.get(self.u1id)
            self.assertEqual(updated_user.username, 'sokkanew')
            self.assertEqual(updated_user.email, 'sokkanew@email.com')
            self.assertTrue(updated_user.check_password('newpassword'))
            

        

           

           


