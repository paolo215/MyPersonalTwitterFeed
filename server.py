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


app = Flask(__name__, static_url_path='/static')

# Get these info by creating twitter app
CONSUMER_KEY = config.CONSUMER_KEY
CONSUMER_SECRET = config.CONSUMER_SECRET
ACCESS_KEY = config.ACCESS_KEY
ACCESS_SECRET = config.ACCESS_SECRET


filename = "follow.txt"
delim = ";"

@app.route("/")
def index():
    follow_users = []
    if "follow" in request.cookies:
        follow_users = get_follow_users()

    feeds = get_all_timelines(follow_users)
    return render_template("index.html", getFeed=getFeed, follow_users=follow_users, feeds=feeds)


@app.route("/profile/<screen_name>")
def getFeed(screen_name):
    follow_users = []
    if "follow" in request.cookies:
        follow_users = get_follow_users()



    timeline = get_timeline(screen_name)
    return render_template("profile/index.html", timelines={screen_name: timeline}, follow_users=follow_users, getFeed=getFeed)


@app.route("/addUser", methods=["POST"])
def addUser():
    follow_users = []
    response = make_response(redirect("/"))
    if "follow" in request.cookies:
        follow_users = get_follow_users()
    else:
        response.set_cookie("follow", "")


    if request.form["user"] and not request.form["user"] in follow_users:
        response.set_cookie("follow", delim.join(follow_users + [request.form["user"]]))

    return response



# https://dev.twitter.com/oauth/overview/single-user
def oauth_req(url, key, secret, http_method="GET", post_body="", http_headers=None):
    consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    response, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
    return json.loads(content)


def get_all_timelines(follow_users):
    feeds = []
    for user in follow_users:
        timeline = get_timeline(user)
        feeds += timeline

    return reversed(sorted(feeds, key=lambda x: datetime.datetime.strptime(x["created_at"], "%a %b %d %H:%M:%S +0000 %Y")))


def get_timeline(screen_name):
    timeline = oauth_req("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=25" % screen_name, ACCESS_KEY, ACCESS_SECRET)
    return timeline 



def get_follow_users():
    follow_users = []
    if "follow" in request.cookies:
        follow_users = request.cookies["follow"]
        follow_users = follow_users.split(delim)
    
    return follow_users


"""
def extract_following(filename):
    log = open(filename, "r")
    data = log.read().split("\n")
    data = [f for f in data if f]
    log.close()
    return data
"""

def main():
    port = 5000
    server = WSGIServer(("", port), app)
    print("port: " + str(port))

         
    server.serve_forever()


if __name__ == "__main__":
    main()
