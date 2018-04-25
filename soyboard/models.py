# FIXME: primary key being avoided because you have to do
# some annoying copypaste code to get primary keys to show
import os
import base64
import pathlib
import datetime
from typing import Tuple, Union
from urllib.parse import urlparse

import scrypt
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image

from . import config


db = SQLAlchemy()

# FIXME: move to config
THUMBNAIL_SIZE_OP = 250, 250
THUMBNAIL_SIZE_REPLY = 125, 125


# FIXME: bad schema...
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(120))
    name = db.Column(db.String(120))
    tripcode = db.Column(db.String(64))
    message = db.Column(db.String(120), nullable=False)
    image = db.Column(db.String(120))
    tip_link = db.Column(db.String(120))
    tip_domain = db.Column(db.String(120))
    thumbnail = db.Column(db.String(120))
    reply_to = db.Column(db.Integer, db.ForeignKey('posts.id'))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    bumptime = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    @staticmethod
    def format_message(message: str) -> str:
        """Parse #id links and break blocks into paragraphs."""
        # last step: strip everything but specific link kind and paragraphs
        # and make sure there's no stle or anything
        pass

    # FIXME: what if passed a name which contains no tripcode?
    @staticmethod
    def make_tripcode(name_and_tripcode: str) -> Tuple[str, str]:
        """Create a tripcode from the name field of a post.

        Returns:
            tuple: A two-element tuple containing (in the order of):
                name without tripcode, tripcode.

        Warning:
            Must have `this#format` or it will raise an exception
            related to unpacking.

        """

        name, unhashed_tripcode = name_and_tripcode.split('#', 1)
        tripcode = str(
            base64.b64encode(
                scrypt.hash(unhashed_tripcode, config.SECRET_KEY),
            ),
        )[2:22]
        return name, tripcode

    @staticmethod
    def tip_link_stuff(tip_link: str) -> Tuple[Union[str, None], Union[str, None]]:
        if not tip_link:
            return None, None
        elif (not tip_link.startswith('http://')) or (not tip_link.startswith('https://')):
            tip_link = 'http://' + tip_link

        tip_domain = urlparse(tip_link).hostname if tip_link else None
        return tip_link, tip_domain

    @classmethod
    def from_form(cls, form):
        """Create and return a Post.

        The form may be a reply or a new post.

        Returns:
            Post: ...

        """

        # A valid tripcode is a name field containing an octothorpe
        # that isn't the last character.
        if form.name.data and '#' in form.name.data[:-1]:
            name, tripcode = cls.make_tripcode(form.name.data)
            is_verified = VerifiedTripcode.is_verified(tripcode)
        else:
            name = form.name.data
            tripcode = None
            is_verified = False

        # If starting a thread or has image and NOT verified make
        # error (new threads require an image so this is implicit)
        if any([form.image.data, form.tip_link.data]) and not is_verified:
            raise Exception('Verified tripcode error.')

        # NOTE: not a fan of doing this, but there's really no
        # other way to get url and abs path to static directory
        # than importing the app! If we import it out of this
        # method's scope, we'll get a circular dependency, also.
        from . import app

        # First we handle image if there is one (optional for replies)
        if form.image.data and is_verified:
            # NOTE: what if overwrite error
            safe_name = secure_filename(form.image.data.filename)
            upload_url = os.path.join(
                app.app.static_url_path,
                'uploads',
                safe_name,
            )
            upload_abs_path = os.path.join(
                app.app.static_folder,
                'uploads',
                safe_name,
            )
            form.image.data.save(upload_abs_path)

            # thumbnail
            # FIXME: make into method
            image = Image.open(upload_abs_path)
            if hasattr(form, 'reply_to'):
                image.thumbnail(THUMBNAIL_SIZE_REPLY)
            else:
                image.thumbnail(THUMBNAIL_SIZE_OP)
            thumbnail_url = os.path.join(
                app.app.static_url_path,
                'thumbnails',
                ('%dx%d' + safe_name) % image.size,
            )
            thumbnail_abs_path = os.path.join(
                app.app.static_folder,
                'thumbnails',
                ('%dx%d' + safe_name) % image.size,
            )
            image.save(thumbnail_abs_path)
        else:
            upload_url = None
            thumbnail_url = None

        tip_link, tip_domain = cls.tip_link_stuff(form.tip_link.data)
        new_post = cls(
            subject=form.subject.data,
            name=name,
            tripcode=tripcode,
            tip_link=tip_link,
            tip_domain=tip_domain,
            image=upload_url,
            thumbnail=thumbnail_url,
            message=form.message.data,
            reply_to=getattr(form, 'reply_to').data if hasattr(form, 'reply_to') else None,
        )
        db.session.add(new_post)
        db.session.commit()

        if hasattr(form, 'reply_to'):
            original = db.session.query(Post).get(new_post.reply_to)
            original.bumptime = datetime.datetime.utcnow()
            db.session.commit()

        return new_post


# Create user model.
# TODO: rename admin?
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(200))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
    # Required for administrative interface
    def __unicode__(self):
        return self.username


class Ban(db.Model):
    """Admin can ban by address or network."""
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), unique=True)
    reason = db.Column(db.String(100))

    @classmethod
    def from_form(cls, form):
        new_ban = cls(
            address=form.address.data,
            reason=form.reason.data,
        )
        db.session.add(new_ban)
        db.session.commit()

        return new_ban


class SiteBanner(db.Model):
    """Randomly rotated banners."""
    id = db.Column(db.Integer, primary_key=True)
    src = db.Column(db.String(100), unique=True)


class ErrorPageImage(db.Model):
    """Randomly rotated error images."""
    id = db.Column(db.Integer, primary_key=True)
    src = db.Column(db.String(100), unique=True)


class BlotterEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)


class VerifiedTripcode(db.Model):
    """Tripcodes are just tripcodes which explicitly allowed
    to post images and start threads.

    Sha256 tripcodes.

    """

    tripcode = db.Column(db.String(20), primary_key=True)  # tripcode

    @staticmethod
    def is_verified(tripcode_to_check: str) -> bool:
        return bool(
            db.session.query(VerifiedTripcode).get(tripcode_to_check)
        )


class ConfigPair(db.Model):
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(100))
