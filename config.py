# SQLALCHEMY_DATABASE_URI = 'postgresql:///videogame_library'
import os
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
SECRET_KEY = "Keep it secret, keep it safe.."
DEBUG_TB_INTERCEPT_REDIRECTS = False