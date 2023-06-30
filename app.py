from flask import Flask, redirect, request, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import ItegrityError

from models import db, connect_db, 
from forms import

app = Flask(__name__)

app.config.from_object("config")
connect_db(app)

debug = DebugToolbarExtension(app)

@app.route('/')


# response = requests.get(f'https://api.exchangerate.host/convert?from={first_curr}&to={second_curr}&amount={amount}&places=2')
# https://api.rawg.io/api/creators/{id}
# https://api.rawg.io/api/creators