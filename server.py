from flask import Flask
from flask import render_template
from gevent.wsgi import WSGIServer
import oauth2
import config
import json
import requests


app = Flask(__name__, static_url_path='/static')

# Get these info by creating twitter app
CONSUMER_KEY = config.CONSUMER_KEY
CONSUMER_SECRET = config.CONSUMER_SECRET
ACCESS_KEY = config.ACCESS_KEY
ACCESS_SECRET = config.ACCESS_SECRET

# Sort users in alphebetical order 
follow_users = sorted(["realDonaldTrump", "twitterapi"])


@app.route("/")
def index():
    return render_template("index.html", getFeed=getFeed, follow_users=follow_users)


@app.route("/follow/<screen_name>")
def getFeed(screen_name):
    timeline = getTimeline(screen_name)
    log = open("log.json", "w")
    json.dump(timeline,log)
    log.close()
    return render_template("follow/index.html", timelines={screen_name: timeline}, follow_users=follow_users, getFeed=getFeed)



# https://dev.twitter.com/oauth/overview/single-user
def oauth_req(url, key, secret, http_method="GET", post_body="", http_headers=None):
    consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    response, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
    return json.loads(content)

def getTimeline(screen_name):
    timeline = oauth_req("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=%s&count=25" % screen_name, ACCESS_KEY, ACCESS_SECRET)
    return timeline 

def main():
    server = WSGIServer(("", 5000,), app)
    server.serve_forever()


if __name__ == "__main__":
    main()
