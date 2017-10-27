"""
    Paolo Villanueva

    Created: June 7th, 2017

"""
from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import make_response
from gevent.wsgi import WSGIServer
import oauth2
import config
import json
import os
import requests
import datetime


# Instantiate Flask app
app = Flask(__name__, static_url_path='/static')

# Get these info by creating a twitter application
# https://apps.twitter.com
CONSUMER_KEY = config.CONSUMER_KEY
CONSUMER_SECRET = config.CONSUMER_SECRET
ACCESS_KEY = config.ACCESS_KEY
ACCESS_SECRET = config.ACCESS_SECRET


# Delimiter for bookmarking users
delim = ";"



@app.route("/")
def index():
    """
    Renders the index page which shows all users' recent twitter posts
    """
    follow_users = []
    if "follow" in request.cookies:
        follow_users = get_follow_users()

    # Get all timelines
    feeds = get_all_timelines(follow_users)

    # Render index page
    return render_template("index.html", getFeed=getFeed, follow_users=follow_users, feeds=feeds)


@app.route("/profile/<screen_name>")
def getFeed(screen_name):
    """ 
    Renders profile page which shows the user's recent twitter posts
    """

    follow_users = []
    if "follow" in request.cookies:
        follow_users = get_follow_users()


    # Get user's timeline
    timeline = get_timeline(screen_name)

    # Render profile page for the user
    return render_template("profile/index.html", timelines={screen_name: timeline}, follow_users=follow_users, getFeed=getFeed)


@app.route("/addUser", methods=["POST"])
def addUser():
    """
    POST request - used for bookmarking a user.
    Redirects to index page.
    """


    follow_users = []
    response = make_response(redirect("/"))

    # If "follow" key exists in cookies, get all users
    # Otherwise, set it to empty
    if "follow" in request.cookies:
        follow_users = get_follow_users()
    else:
        response.set_cookie("follow", "")

    # Add user to "follow"
    if request.form["user"] and not request.form["user"] in follow_users:
        response.set_cookie("follow", delim.join(follow_users + [request.form["user"]]))

    return response



# https://dev.twitter.com/oauth/overview/single-user
def oauth_req(url, key, secret, http_method="GET", post_body="", http_headers=None):
    """
    Authenticate access to the API using OAuth.
    """
    consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    response, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
    return json.loads(content)


def get_all_timelines(follow_users):
    """
    Returns all the users' timelines
    """
    feeds = []
    for user in follow_users:
        timeline = get_timeline(user)
        feeds += timeline

    # Organize posts by date
    return reversed(sorted(feeds, key=lambda x: datetime.datetime.strptime(x["created_at"], "%a %b %d %H:%M:%S +0000 %Y")))


def get_timeline(screen_name):
    """
    Get user's timeline
    """
    timeline = oauth_req("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=25" % screen_name, ACCESS_KEY, ACCESS_SECRET)
    return timeline 



def get_follow_users():
    """
    Get all the users stored in the cookie
    """
    follow_users = []
    if "follow" in request.cookies:
        follow_users = request.cookies["follow"]
        follow_users = follow_users.split(delim)
    
    return follow_users


def main():
    port = 5000

    # Set up WSGI Server and use Flask as middleware
    server = WSGIServer(("", port), app)
    print("port: " + str(port))

    
    # Start server
    server.serve_forever()


if __name__ == "__main__":
    main()
