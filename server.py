from flask import Flask
from flask import render_template
from gevent.wsgi import WSGIServer
import oauth2
import config
import json

app = Flask(__name__)


CONSUMER_KEY = config.CONSUMER_KEY
CONSUMER_SECRET = config.CONSUMER_SECRET
ACCESS_KEY = config.ACCESS_KEY
ACCESS_SECRET = config.ACCESS_SECRET

targets = ["realDonaldTrump"]
timelines = {}

@app.route("/")
def index():
    print(timelines)
    return render_template("index.html", timelines=timelines)


# https://dev.twitter.com/oauth/overview/single-user
def oauth_req(url, key, secret, http_method="GET", post_body="", http_headers=None):
    consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    response, content = client.request(url, method=http_method, body=post_body, headers=http_headers)
    return json.loads(content)

def main():
    server = WSGIServer(("", 5000,), app)
    for target in targets:
        timeline = oauth_req("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=realDonaldTrump&count=2", ACCESS_KEY, ACCESS_SECRET)
        timelines[target] = timeline
    server.serve_forever()


if __name__ == "__main__":
    main()
