import os
import pprint
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

scope = 'user-follow-read'
spotipy_client_id = os.getenv('SPOTIPY_CLIENT_ID')
spotipy_client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope))
pp = pprint.PrettyPrinter(indent=4)


@ app.route('/api/get-user', methods=['GET'])
def get_user():
    return sp.current_user()


@ app.route('/api/get-artists', methods=['GET'])
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
    for item in artistsJson['artists']:
        albumsAndSingles = []
        albumResults = sp.artist_albums(item['id'], 'album', limit=10)
        albumsAndSingles.extend(albumResults['items'])
        singlesResults = sp.artist_albums(item['id'], 'single', limit=10)
        albumsAndSingles.extend(singlesResults['items'])
        seenAlbums = set()
        uniqueAlbums = []
        for obj in albumsAndSingles:
            if obj['name'] not in seenAlbums:
                uniqueAlbums.append(obj)
                seenAlbums.add(obj['name'])
        item['albums'] = uniqueAlbums
    return artistsJson


@ app.route('/', methods=['GET'])
def index():
    return "<h1>Spotipy New Releases Server</h1>"


if __name__ == '__main__':
    print(datetime.date(datetime.now()))
    app.run(threaded=True, port=5000)
