import requests
from bs4 import BeautifulSoup
from decouple import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth

time_period = input("What time would you like to travel to? (Format as YYYY-MM-DD) ")

URL = f"https://www.billboard.com/charts/hot-100/{time_period}/"

SPOTIPY_CLIENT_ID = config("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = config("CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]

response = requests.get(URL).text
soup = BeautifulSoup(response, "html.parser")

songs = soup.find_all(name="h3", class_="a-no-trucate")
song_list = [song.getText().strip() for song in songs]

song_URIs = []
year = time_period.split("-")[0]

playlist = sp.user_playlist_create(user=f"{user_id}", name=f"{time_period} Billboard Top Tracks", public=False,
                                      description=f"Top 100 Billboard Tracks from {time_period}")

for song in song_list:
    song_found = sp.search(q=f"track: {song} year: {year}", type="track")
    try:
        uri = song_found["tracks"]["items"][0]["uri"]
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")
    else:
        song_URIs.append(uri)
        
sp.playlist_add_items(playlist_id=playlist["id"], items=song_URIs)