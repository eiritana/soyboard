import os

SECRET_KEY = "lol"
SQLALCHEMY_DATABASE_URI = os.environ.get('DB_STRING', 'sqlite:///test.db')
SITE_TAGLINE = 'some tagline'
SITE_TITLE = 'super title'
SITE_FOOTER = '<a href="https://github.com/lily-mayfield/soyboard">Powered by Soyboard</a>'
POSTS_PER_PAGE = 10
INDEX_REPLIES_PER_POST = 3
