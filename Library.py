import spotipy
import spotipy.util
import os


class Song:
    def __init__(self, id, artist, genres):
        self.id = id
        self.artist = artist
        self.genres = genres


class Artist:
    def __init__(self, uri, genres):
        self.genres = genres
        self.uri = uri


class Library:
    def __init__(self, spotify: spotipy.Spotify, mod="genre_"):
        self.artists = set()
        self.songs = set()
        self.genres = dict()
        self.playlists = dict()
        self.modifier = mod
        self.spot = spotify

    # Retrieve all of the spotify users tracks
    def get_tracks(self):
        tracks = self.spot.current_user_saved_tracks(limit=50)
        # get tracks and thier genres
        print("Finding Tracks")
        count = 0
        while tracks is not None:
            self.clear_screen()
            print('Finding Tracks: {}'.format(count))
            count += 50
            for item in tracks['items']:
                # check cache
                track_genres = self.cache_artist_genres(item['track']['artists'][0]['uri'])
                for genre in track_genres:
                    if genre in self.genres:
                        self.genres[genre] += 1
                    else:
                        self.genres[genre] = 1
                self.songs.add(Song(item['track']['id'], item['track']['artists'][0]['uri'], track_genres))
            tracks = self.spot.next(tracks)

    def cache_artist_genres(self, uri):
        for artist in self.artists:  # get info from cache
            if artist.uri == uri:
                track_genres = artist.genres
                break
        else:  # get info from spotify
            artist_genres = self.spot.artist(uri)['genres']
            self.artists.add(Artist(uri, artist_genres))
            track_genres = artist_genres
        return track_genres

    def match_playlists(self, sg: list):
        # create list of users playlists
        print("Finding existing playlists")
        play_obj = self.spot.current_user_playlists()
        while play_obj is not None:
            for pl in play_obj['items']:
                genre = pl['name'][len(self.modifier):]
                if genre in sg:
                    self.playlists[genre] = pl['id']
            play_obj = self.spot.next(play_obj)

    def create_playlists(self, sg):
        # create genre playlists
        print("Creating Playlists")
        user_obj = self.spot.current_user()
        uid = user_obj['id']
        play_url = "https://api.spotify.com/v1/users/{}/playlists/".format(uid)
        for genre in sg:
            # does playlist exist?
            if genre not in self.playlists:
                # create playlist
                payload = {
                    "name": self.modifier+genre,
                    "public": False,
                    "description": "Created by Spotify-Genre-Sorter"
                }
                # use _get to access spot api to create playlist
                # this is a private function but Python can't tell me how to live my life
                result = self.spot._post(play_url, payload=payload)
                self.playlists[genre] = result['id']

    def update_playlists(self, sg: list):
        self.match_playlists(sg)
        self.create_playlists(sg)
        user_obj = self.spot.current_user()
        uid = user_obj['id']
        # add tracks to respective genres# convert to tuple
        print("Filling out playlists")
        track_queue = dict()
        for genre in sg:  # [genre,[id's]]
            track_queue[genre] = list()
        print("Sorting tracks to add")
        for count, track in enumerate(self.songs):
            if count % 50 == 0:
                self.clear_screen()
                print("Processed {} out of {} tracks".format(count, len(self.songs)))
            for genre in sg:
                if genre in track.genres:
                    track_queue[genre].append(track.id)
        for genre, play_tracks in track_queue.items():
            print("Processing {}".format(genre))
            while len(play_tracks) > 0:
                self.spot.user_playlist_add_tracks(uid, self.playlists[genre], play_tracks[:50])
                del play_tracks[:50]

    # Utility function to clear terminal screen
    @staticmethod
    def clear_screen():
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')