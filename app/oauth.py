from flask import flash
from flask_login import current_user, login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_pymongo import PyMongo, ObjectId
import os

blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    offline=True,
    reprompt_consent=True
    )

def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return False

    info = resp.json()

    # Find this OAuth token in the database, or create it
    try:
        oauth = find_email(info['email'])
    except:
        print("User not found")
    else:
        oauth = info | token
        ct.insert(oauth)

    login_user(User(oauth['email']))

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False

# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, message, response):
    msg = ("OAuth error from {name}! " "message={message} response={response}").format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")