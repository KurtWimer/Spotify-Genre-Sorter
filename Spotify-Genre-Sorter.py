import spotipy
import spotipy.util
import time

from os import system, name
from time import sleep
# Know Bugs
# returning empty for playlists
# cached profiles interfere with each toher
# must double press enter on authentification

# desired features
# cache artist genre info
# add tracks in batches
def main():
    spot_obj = authenticate()
    track_genre = get_tracks(spot_obj) # tuple of (tracks,genres)
    selected_genres = select_genres(track_genre[1])
    genre_id = match_playlists(spot_obj, selected_genres) # tuple of (str genre, str plid)
    update_playlists(spot_obj, genre_id, track_genre[0])
    print('Success')

def clear_scrn():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')


def authenticate() -> spotipy.Spotify:
    # DO NOT LEAVE IF POSTED TO GITHUB
    client_id = '392baf4fd4ab42c994f5c0959f9d57c7'
    client_secret = 'd8b2569fdd7b4a4babfe2325069b34da'
    # DO NOT LEAVE IF POSTED TO GITHUB

    redirect_uri = 'http://localhost/'
    scope = 'user-library-read playlist-modify-private playlist-read-collaborative playlist-read-private'
    username = input('Please enter username: ')
    print('Attempting to authenticate {}:'.format(username))
    token = spotipy.util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret,
                                               redirect_uri=redirect_uri)
    if token:
        print("Succesfull Authentification")
        # create spotify object
        spot = spotipy.Spotify(auth=token)
    else:
        print('Failure to validate token')
        exit(code=1)
    return spot


# return values: (track_list, genre_set)
def get_tracks(spot: spotipy.Spotify) -> tuple:
    tracks = spot.current_user_saved_tracks(limit=50)
    # get tracks and thier genres
    print("Finding Tracks")
    genre_set = set()
    track_list = list()
    count = 0
    while tracks is not None:
        clear_scrn()
        print('Finding Tracks{}'.format(count))
        count +=50
        for item in tracks['items']:
            artist_info = spot.artist(item['track']['artists'][0]['uri'])
            artist_genres = artist_info['genres']
            for genre in artist_genres:
                genre_set.add(genre)
            track_list.append([item['track']['name'], item['track']['id'], artist_genres])
        tracks = spot.next(tracks)
    returnval = (track_list, genre_set)
    return returnval


def select_genres(genre_set: set) -> list:
    # select genres
    print('Here are your music genres: ')
    time.sleep(1)
    for genre in genre_set:
        print(genre)
    sg_string = input("Please type selected genres in a comma seperated list\n"
                      "Example: Rock,  deep underground hip hop, brostep\n")
    selected_genres = sg_string.split(',')
    # remove trailing whitespace
    selected_genres = ['genre_{}'.format(genre.strip()) for genre in selected_genres]
    return selected_genres


# paramaters: spotify object, selected genres list
# returns: a list of tuples formated as follows (genre, playlist id)
def match_playlists(spot: spotipy.Spotify, sg: list) ->list:
    # create list of users playlists
    print("Finding existing playlists")
    play_obj = spot.current_user_playlists()
    sg_tup= sg
    while play_obj is not None:
        for playlist in play_obj['items']:
            try:
                index = sg.index(playlist['name'])
                # change list to contain tuple (genre, uri)
                sg_tup[index] = (sg[index], playlist['id'])
            except ValueError:
                continue
        play_obj = spot.next(play_obj)
    # create genre playlists
    print("Updating/Creating Playlists")
    user_obj = spot.current_user()
    uid = user_obj['id']
    play_url = "https://api.spotify.com/v1/users/{}/playlists/".format(uid)
    for i, genre in enumerate(sg_tup):
        # does playlist exist?
        if type(genre) is str:
            # create playlist
            payload = {
                "name": genre,
                "public": False,
                "description": "Created by Spotify-Genre-Sorter"
            }
            # use _get to acess spot api to create playlist
            # this is a private function but Python can't tell me how to live my life
            result = spot._post(play_url, payload=payload)
            # convert to tuple
            sg_tup[i] = (genre, result['id'])
    return sg_tup


def update_playlists(spot: spotipy.Spotify,sg_tup: list, tracks: list):
    user_obj = spot.current_user()
    uid = user_obj['id']
    # add tracks to respective genres
    print("Filling out playlists")
    count = 0
    for track in tracks:
        if count%25==0:
            clear_scrn()
            print("Processed {} out of {} tracks".format(count, len(tracks)))
        count += 1
        for play_genre in sg_tup:
            for genre in track[2]:
                if play_genre[0][6:] == genre: # must removve the tag before comparison
                    # todo ideally I should add in batches of <=50
                    spot.user_playlist_add_tracks(uid, play_genre[1], [track[1]])


if __name__ == '__main__':
    main()






