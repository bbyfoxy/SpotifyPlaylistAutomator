import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

os.system("pip install -r REQUIREMENTS.txt")
os.system("cls")

def getUserCredentials():
    print("PLEASE READ THE TUTORIAL SECTION OF THE README.md FILE")
    clientId = input("Please enter your Spotify Client ID: ")
    clientSecret = input("Please enter your Spotify Client Secret: ")
    redirectUri = "http://127.0.0.1:8888/callback"
    with open("credentials.json", "w") as credFile:
        json.dump([
            clientId,
            clientSecret,
            redirectUri
        ], credFile)
    print("Credentials saved to credentials.json")

def createNewPlaylist(SP):
    name = input("____________________\nEnter the name of the new playlist: \n")
    privacy = input("Should the playlist be public or private? (Enter 'True' for public, 'False' for private): \n")
    if privacy.lower() == 'true':
        privacy = True
    elif privacy.lower() == 'false':
        privacy = False
    else:
        print("Invalid input. Please enter 'True' or 'False'.")
        createNewPlaylist(SP)
        return
    description = input("Enter a description for the playlist: \n")
    # name, privacy, description, SP
    try:
        SP.user_playlist_create(SP.current_user()["id"], name, privacy, False, description)
        print("Playlist ", name, " created successfully!\nYou can now add songs to it from the start menu.")
        main() # Return to main menu
        return
    except Exception as e:
        print("An error occurred while creating the playlist, are you sure your inputs fit the parameters?\n", e)
        createNewPlaylist(SP) # Retry creating playlist
        return

def addToExistingPlaylist(SP):
    name = input("____________________\nEnter the name of the playlist you want to add songs to: \n")
    playlists = SP.current_user_playlists()
    playlistID = None

    playlistFound = False
    for playlist in playlists.get("items"):
        if playlist.get("name").lower() == name.lower():
            print("Found playlist: ", playlist.get("name"))
            playlistFound = True
            playlistID = playlist.get("id")
            break
    if not playlistFound:
        print("Playlist not found. Please check the name and try again.")
        addToExistingPlaylist(SP)
        return
    
    artistName = input("Write the name of the artist whose albums/EPs you would like to add\n")
    try:
        results = SP.search(q=artistName, type="artist")
        artistID = results.get("artists").get("items")[0].get("uri")
        print("____________________\nAlbums/EPs by ", artistName, ":")
        artistAlbums = {}
        n = 1
        # Fetching albums
        for item in SP.artist_albums(artistID, album_type="album").get("items"):
            print(n, ". ", item.get("name"))
            artistAlbums[n] = item.get("name")
            n += 1
        # Fetching EPs
        for item in SP.artist_albums(artistID, album_type="single").get("items"):
            if item.get("total_tracks") > 1:
                print(n, ". ", item.get("name"))
                artistAlbums[n] = item.get("name")
                n += 1
        uInput = input("____________________\nPlease write the number(s) of your selected items seperated by '.' or type '0' to add all\n")
        trackUris = []
        # Chunked function to handle adding more than 100 tracks at once because api only allows requests of 100 at a time
        def chunked(iterable):
            for i in range(0, len(iterable), 100):
                yield iterable[i:i + 100]
        if uInput == "0":
            # Add all tracks from all albums
            for album in SP.artist_albums(artistID, album_type="album").get("items"):
                albumID = album.get("id")
                tracks = SP.album_tracks(albumId).get("items", [])
                for track in tracks:
                    trackUris.append(track.get("uri"))
            # Add all tracks from all EPs
            for album in SP.artist_albums(artistID, album_type="single").get("items"):
                if album.get("total_tracks") > 1:
                    albumId = album.get("id")
                    tracks = SP.album_tracks(albumId).get("items", [])
                    for track in tracks:
                        trackUris.append(track.get("uri"))
            try:
                for chunk in chunked(trackUris):
                    SP.playlist_add_items(playlist_id=playlistID, items=chunk, position=None)
                print("All albums/EPs added successfully!")
            except Exception as e:
                print("An error occurred while adding the album(s)/EP(s): ", e)
            main()
            return
        else:
            # Add tracks from selected albums/EPs only
            selectedNumbers = [name.strip() for name in uInput.split(".") if name.strip()]
            selectedAlbums = []
            try:
                for number in selectedNumbers:
                    selectedAlbums.append(artistAlbums.get(int(number)))
            except Exception as e:
                print("An error has occured while processing your input: ", e)
            # Albums
            for album in SP.artist_albums(artistID, album_type="album").get("items"):
                if album.get("name") in selectedAlbums:
                    albumId = album.get("id")
                    tracks = SP.album_tracks(albumId).get("items", [])
                    for track in tracks:
                        trackUris.append(track.get("uri"))
            # EPs
            for album in SP.artist_albums(artistID, album_type="single").get("items"):
                if album.get("name") in selectedAlbums:
                    albumId = album.get("id")
                    tracks = SP.album_tracks(albumId).get("items", [])
                    for track in tracks:
                        trackUris.append(track.get("uri"))
            if trackUris:
                try:
                    for chunk in chunked(trackUris):
                        SP.playlist_add_items(playlist_id=playlistID, items=chunk, position=None)
                    print("Selected albums/EPs added successfully!")
                except Exception as e:
                    print("An error occurred while adding the selected album(s)/EP(s): ", e)
            else:
                print("No matching albums/EPs found")
    except Exception as e:
        print("An error occurred: ", e)

# MAIN FUNCTION
def main():
    # Welcome message and user input for Spotify credentials
    print("____________________\nWelcome to the Spotify Project!")
    try:
        with open("credentials.json", "r") as credFile:
            data = json.load(credFile)
            print("Loaded saved Spotify credentials.")
    except FileNotFoundError:
        getUserCredentials()
        with open("credentials.json", "r") as credFile:
            data = json.load(credFile)

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=data[0], client_secret=data[1], redirect_uri=data[2], scope="playlist-modify-public playlist-modify-private"))

    uInput = input("What would you like to do?\n1. Create a new playlist\n2. Add to an existing playlist (Only mass adding tracks from artists is supported)\n3. Quit\n")
    if uInput == "1":
        createNewPlaylist(sp)
    elif uInput == "2":
        addToExistingPlaylist(sp)
    elif uInput == "3":
        pass # Quits program
    else:
        print("Invalid input. Please enter 1 or 2.")

main()