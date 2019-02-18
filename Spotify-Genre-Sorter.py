import spotipy
import spotipy.util
import time
import Library

from os import system, name


# desired features
# add tracks in batches
# get genres from album instead of artist?

# Retrieve all tracks, sort by genre, create/update playlists based upon user selection
def main():
    spot_obj = authenticate()
    lib = Library(spot_obj)
    lib.get_tracks()  # tuple of (tracks,genres in dictionary containing frequency)
    selected_genres = select_genres(lib.genres)
    lib.update_playlists(selected_genres)
    print('Success')


# Authenticate spotify user
def authenticate() -> spotipy.Spotify:
    # DO NOT LEAVE IF POSTED TO GITHUB
    client_id = "e03655052013460a9b7800da563d0af0"
    client_secret = "46e7e7acd85f4d67b4c51149c54e85cd"
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
        return spot
    else:
        print('Failure to validate token')
        exit(code=1)


def select_genres(genres: dict) -> list:
    # select genres
    while True:
        try:
            min = int(input("Please input a minimum song number to display genres for: "))
            break
        except ValueError:
            print("Expected Integer")
            continue
    print('Here are your music genres: ')
    time.sleep(1)
    for genre in sorted(genres):
        if genres[genre] >= min:
            print(genre)
    sg_string = input("Please type selected genres in a comma seperated list\n"
                      "Example: Rock, deep underground hip hop, brostep\n")
    selected_genres = sg_string.split(",")
    # remove trailing whitespace
    selected_genres = [format(genre.strip()) for genre in selected_genres]
    return selected_genres


if __name__ == '__main__':
    main()
