import os
import time
import sys
import pprint
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
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

app = Flask(__name__)
app.secret_key = os.getenv('SECRET')

scope = 'user-follow-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
pp = pprint.PrettyPrinter(indent=4)


@app.route('/api/get-user', methods=['GET'])
def get_user():
    user = sp.current_user()
    return user


@app.route('/api/get-artists', methods=['GET'])
def get_artists():
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
        albumResults = sp.artist_albums(item['id'], 'album', limit=10)
        albumsAndSingles.extend(albumResults['items'])
        singlesResults = sp.artist_albums(item['id'], 'single', limit=10)
        albumsAndSingles.extend(singlesResults['items'])
        item['albums'] = albumsAndSingles
    return artistsJson


@app.route('/', methods=['GET'])
def index():
    return "<h1>Spotipy New Releases Server</h1>"


if __name__ == '__main__':
    print(datetime.date(datetime.now()))
    app.run(threaded=True, port=5000)
