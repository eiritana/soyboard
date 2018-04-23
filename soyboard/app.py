# TODO: limiter, caching
import os
import random

from flask import (
    Flask, redirect, render_template, url_for, send_from_directory, request, send_file
)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from . import forms
from . import config
from . import models
from . import moderate


app = Flask(__name__)
app.config.from_object(config)


def config_db(key: str) -> str:
    return models.ConfigPair.query.get(key).value


@app.route("/", methods=['GET'])
def board_index():
    """View the posts (paginated).

    """

    form = forms.NewPostForm()
    current_page = request.args.get('page', type=int) or 1
    pages = (
        models.Post.query.filter(models.Post.reply_to == None)
        .order_by(models.Post.bumptime.desc())
        .paginate(
            current_page,
            per_page=config.POSTS_PER_PAGE,
        )
    )
    total_pages = pages.pages
    posts = pages.items
    # FIXME: should just use backref relationship
    for post in posts:
        replies = reversed(
            (
                models.Post.query
                .filter(models.Post.reply_to == post.id)
                .order_by(models.Post.id.desc())
                .limit(config.INDEX_REPLIES_PER_POST)
                .all()
            )
        )
        post.replies = replies

    return render_template(
        'board-index.html',
        form=form,
        posts=posts,
        total_pages=total_pages,
        current_page=current_page,
        blotter_entries=get_blotter_entries(),
    )


# FIXME: check if reply or not for error/404, else...
@app.route("/posts/<int:post_id>")
def view_specific_post(post_id: int):
    """..."""

    form = forms.NewReplyForm()
    post = models.db.session.query(models.Post).get(post_id)
    replies = models.db.session.query(models.Post).filter(models.Post.reply_to == post_id)
    return render_template(
        'post.html',
        form=form,
        post=post,
        replies=replies,
        blotter_entries=get_blotter_entries(),
    )


@app.route("/posts/delete")
def delete_post():
    """Delete a series of posts by ID separated by commas.

    Must be post author *or* admin to delete.

    """

    pass


# FIXME must check if conflicting slug...
# what if making reply but reply is a comment?!
@app.route("/posts/new", methods=['POST'])
def create_post():
    """..."""

    # First check if IP banned
    ban = moderate.ban_lookup(request)
    if ban:
        ban_message = 'Your IP %s was banned: %s' % (ban.address, ban.reason)
        return render_template('errors.html', errors=[ban_message])

    reply_to = request.form.get('reply_to')
    print(reply_to)
    if reply_to:
        form = forms.NewReplyForm()
    else:
        form = forms.NewPostForm()

    if form.validate_on_submit():
        post = models.Post.from_form(form)
        if post.reply_to:
            return redirect(
                url_for(
                    'view_specific_post',
                    post_id=post.reply_to,
                    _anchor=post.id,
                )
            )
        else:
            return redirect(
                url_for(
                    'view_specific_post',
                    post_id=post.id,
                )
            )

    # FIXME: this should be an error because something
    # failed wtforms validation.
    errors = []
    for field, field_errors in form.errors.items():
        field_name = getattr(form, field).label.text
        for error in field_errors:
            errors.append("%s: %s" % (field_name, error))
    return render_template('errors.html', errors=errors)


@app.route("/error-page-image")
def error_page_image():
    """..."""

    random_src = random.randint(
        1,
        models.db.session.query(models.ErrorPageImage).count(),
    )
    src = models.db.session.query(models.ErrorPageImage).get(random_src)
    return send_file(src.src)


@app.route("/site-banner")
def site_banner():
    """..."""

    random_src = random.randint(
        1,
        models.db.session.query(models.SiteBanner).count(),
    )
    src = models.db.session.query(models.SiteBanner).get(random_src)
    return send_file(src.src)


def get_blotter_entries():
    return models.BlotterEntry.query.order_by(models.BlotterEntry.id.desc()).all()


# should go later in app factory...
with app.app_context():
    # Make it so can access config db from template
    app.jinja_env.globals.update(config_db=config_db)

    # Initialize flask-login
    moderate.init_login(app)

    # Create admin
    admin_ = Admin(app, 'Example: Auth', index_view=moderate.MyAdminIndexView(), base_template='my_master.html')

    # Add views
    admin_.add_view(moderate.MyModelView(models.User, models.db.session))
    admin_.add_view(moderate.MyModelThumbView(models.Post, models.db.session))
    admin_.add_view(moderate.MyModelView(models.Ban, models.db.session))
    admin_.add_view(moderate.MyModelSrcView(models.ErrorPageImage, models.db.session))
    admin_.add_view(moderate.MyModelSrcView(models.SiteBanner, models.db.session))
    admin_.add_view(moderate.MyModelView(models.BlotterEntry, models.db.session))
    admin_.add_view(moderate.VerifiedTripcodeView(models.VerifiedTripcode, models.db.session))
    admin_.add_view(moderate.ConfigView(models.ConfigPair, models.db.session))

    models.db.init_app(app)
    moderate.build_sample_db()
