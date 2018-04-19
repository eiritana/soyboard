# TODO: CSRF Protection and validation
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename


class NewPostForm(FlaskForm):
    """Form for creating a new post.

    """

    subject = StringField('Subject')
    name = StringField('Name')
    tip_link = StringField('Tip Link')
    message = TextAreaField('Message', validators=[DataRequired()])
    image = FileField(validators=[FileRequired()])


class NewReplyForm(FlaskForm):
    """Form for creating a new post.

    """

    subject = StringField('Subject')
    name = StringField('Name')
    tip_link = StringField('Tip Link')
    message = TextAreaField('Message', validators=[DataRequired()])
    image = FileField()

    # FIXME: validate that post exists if specified?
    reply_to = HiddenField('reply_to')
