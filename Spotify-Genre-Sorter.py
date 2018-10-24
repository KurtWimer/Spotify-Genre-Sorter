import spotipy
import spotipy.util
import time

# Know Bugs
# returning empty for playlists
# cached profiles interfere with each toher
#

# DO NOT LEAVE IF POSTED TO GITHUB
client_id = '392baf4fd4ab42c994f5c0959f9d57c7'
client_secret = 'd8b2569fdd7b4a4babfe2325069b34da'
redirect_uri = 'http://localhost/'

scope = 'user-library-read playlist-modify-private'
username = raw_input('Please enter username: ')
print('Attempting to authenticate {}:'.format(username))
token = spotipy.util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret,
                                           redirect_uri=redirect_uri)
track_list = []
genre_set = set()
if token:
    print("Succesfull Authentification")
    # create spotify object
    spot = spotipy.Spotify(auth=token)
    tracks = spot.current_user_saved_tracks(limit=50)
    # get tracks and thier genres
    print("Finding Tracks")
    for item in tracks['items']:

        artist_info = spot.artist(item['track']['artists'][0]['uri'])
        artist_genres = artist_info['genres']
        for genre in artist_genres:
            genre_set.add(genre)
        track_list.append([item['track']['name'], item['track']['id'], artist_genres])

    # select genres
    print('Here are your music genres: ')
    time.sleep(2)
    for genre in genre_set:
        print(genre)
    sg_string = raw_input("Please type selected genres in a comma seperated list\n"
                          "Example: Rock,  deep underground hip hop, brostep\n")
    selected_genres = sg_string.split(',')
    # remove trailing whitespace
    for genre in selected_genres:
        genre = genre.split()

    # create list of users playlists
    print("Finding existing playlists")
    play_obj = spot.current_user_playlists()
    while play_obj is not None:
        for playlist in play_obj['items']:
            try:
                index = selected_genres.index(playlist['name'])  # todo figure out why this never evaluates true
                # change list to contain tuple (genre, uri)
                selected_genres[index] = (selected_genres[index], playlist['id'])
            except ValueError:
                continue
        play_obj = spot.next(play_obj)
    # create genre playlists
    print("Updating/Creating Playlists")
    user_obj = spot.current_user()
    uid = user_obj['id']
    play_url = "https://api.spotify.com/v1/users/{}/playlists/".format(uid)
    for i, genre in enumerate(selected_genres):
        # todo figure out why only doing first item
        # does playlist exist?
        if type(genre) is str:
            # create playlist
            payload = {
                "name": "genre_{}".format(genre),
                "public": False,
                "description": "Created by Spotify-Genre-Sorter"
            }
            # use _get to acess spot api to create playlist
            # this is a private function but Python can't tell me how to live my life
            result = spot._post(play_url, payload=payload)
            # convert to tuple
            selected_genres[i] = (genre, result['id'])

    # add tracks to respective genres
    print("Filling out playlists")
    for track in track_list:
        for track_genre in track[2]:
            for genre in selected_genres:  # selected genres is a tuple consisting of name, playlist id
                if genre[0] == track_genre:
                    # todo check if track is already in playlist
                    # todo ideally I should add in batches of <=50
                    spot.user_playlist_add_tracks(uid, genre[1], [track[1]])

else:
    print('Failure to validate token')
