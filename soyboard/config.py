import os

# TODO: config.py.example
SECRET_KEY = "lol"
SQLALCHEMY_DATABASE_URI = os.environ.get('DB_STRING', 'sqlite:////root/test.db')
SITE_TAGLINE = 'some tagline'
SITE_TITLE = 'super title'
SITE_FOOTER = '<a href="https://github.com/malebride/soyboard">Powered by Soyboard</a>'
