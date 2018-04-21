import os

# TODO: config.py.example
SECRET_KEY = "lol"
SQLALCHEMY_DATABASE_URI = os.environ.get('DB_STRING', 'sqlite:///test.db')
SITE_TAGLINE = 'some tagline'
SITE_TITLE = 'super title'
SITE_FOOTER = '<a href="https://github.com/lily-mayfield/soyboard">Powered by Soyboard</a>'
