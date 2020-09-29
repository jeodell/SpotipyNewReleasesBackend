import os
import time
import sys
import pprint
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    request,
    url_for,
    jsonify,
)
from twilio.rest import Client

app = Flask(__name__)

TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

username = os.getenv('USERNAME')
scope = os.getenv('SCOPE')
spotipy_client_id = os.getenv('SPOTIPY_CLIENT_ID')
spotipy_client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
token = util.prompt_for_user_token(
    username, scope, spotipy_client_id, spotipy_client_secret, 'http://localhost:8888/callback/')
sp = spotipy.Spotify(auth=token)
pp = pprint.PrettyPrinter(indent=4)


def get_sent_messages():
    # TODO: Make this return a collection of messages that were sent from the number
    messages = []
    return messages


def send_message(to, body):
    client.messages.create(
        to=to,
        from_=TWILIO_PHONE_NUMBER,
        body=body
    )


@app.route("/time", methods=["GET"])
def get_current_time():
    return {'time': time.time()}


@app.route('/get-user', methods=['GET', 'POST'])
def get_user():
    user = sp.current_user()
    return user


@app.route('/get-artists', methods=['GET', 'POST'])
def get_artists():
    # messages = get_sent_messages()

    followed_artists = sp.current_user_followed_artists(limit=1)

    artistsJson = {
        'artists': []
    }

    while followed_artists:
        artistsJson['artists'].extend(followed_artists['artists']['items'])
        if followed_artists['artists']['next']:
            followed_artists = sp.next(followed_artists['artists'])
        else:
            followed_artists = None
        for i, item in enumerate(artistsJson['artists']):
            albumsAndSingles = []
            albumResults = sp.artist_albums(item['id'], 'album')
            albumsAndSingles.extend(albumResults)
            singlesResults = sp.artist_albums(item['id'], 'single')
            albumsAndSingles.extend(singlesResults)
            item['albums'] = albumsAndSingles
    return artistsJson

    # send_message('+123456789', 'hello')


@ app.route("/add-compliment", methods=["POST"])
def add_compliment():
    print(request.values)
    sender = request.values.get('sender', 'Someone')
    receiver = request.values.get('receiver', 'Someone')
    compliment = request.values.get('compliment', 'wonderful')
    to = request.values.get('to')
    body = f'{sender} says: {receiver} is {compliment}. See more compliments at {request.url_root}'
    # send_message(to, body)
    flash('Your message was successfully sent')
    return redirect(url_for('index'))


if __name__ == '__main__':
    print(datetime.date(datetime.now()))
    app.run(debug=True)
