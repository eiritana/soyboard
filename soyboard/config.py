import os

SECRET_KEY = os.environ.get('SOY_SECRET_KEY', 'PLEASE CHANGE ME')
SQLALCHEMY_DATABASE_URI = os.environ.get('SOY_DB_STRING', 'sqlite:///test.db')
SITE_TAGLINE = os.environ.get('SOY_SITE_TAGLINE', 'some tagline')
SITE_TITLE = os.environ.get('SOY_SITE_TAGLINE', 'super title')
SITE_FOOTER = os.environ.get(
    'SOY_SITE_FOOTER',
    '<a href="https://github.com/lily-mayfield/soyboard">Powered by Soyboard</a>',
)
POSTS_PER_PAGE = int(os.environ.get('SOY_POSTS_PER_PAGE', 10))
INDEX_REPLIES_PER_POST = int(os.environ.get('SOY_INDEX_REPLIES_PER_POST', 3))
