#%%
import json
from spotify import SpotifyAPI,search_track, get_song_parameters, unique, SPOTIFY_API_URL

import genius
import re, requests

import pymongo
from custom_collections import UnknownArtists, Songs, ArtistPlaylist

import datetime

#%%
# Connecting to the db
db_name = "dbspotcred"
mongodb_creds = json.load(open('conf_mongodb.json', 'r'))
# Set client
client = pymongo.MongoClient(
    host='localhost:27017'
)
db = client.dbspotcred
#%%
# Get the APIs keys 
spotify_account = json.load(open('conf_spotify_account.json', 'r'))
spotify_api = SpotifyAPI()
spotify_api.update_token()

# ---------------------------------------------------------------------------- #
#                               Refresh all songs                              #
# ---------------------------------------------------------------------------- #

# --------------- Refresh songs that were not found on Spotify --------------- #
#%%
songs_unavailable = list(db.songs.find({"spotify_uri":{'$exists':False}}))

i=1
n=len(songs_unavailable)
for s in songs_unavailable:
    # print(s["last_update"],type(s["last_update"]))
    # duration = (datetime.datetime.now()-s["last_update"]).total_seconds()
    # printProgressBar(i, n, prefix = 'Progress:', suffix = 'Complete', length = 50)
    print(f"{i}/{n}")
    # print("\n",s["_id"],s["song_name"],"-", s["primary_artist_name"], f'last update : {duration}')

    spotify_song=search_track(track_name=s["song_name"],auth_header=spotify_api.AUTH_HEADER,artist_name=s["primary_artist_name"])
    if spotify_song!={}:
        temp = db.songs.update_one(
            filter={"_id":s["_id"]},
            update={
                "$set": {
                    "spotify_id":spotify_song["id"],
                    "spotify_uri":spotify_song["uri"],
                    "spotify_popularity":spotify_song["popularity"],
                    "last_update": datetime.datetime.utcnow()
                }
            }
        )
    else : 
        temp = db.songs.update_one(
            filter={"_id":s["_id"]},
            update={
                "$set": {
                    "last_update": datetime.datetime.utcnow()
                }
            }
        )
    i+=1
print("Checked all the songs that were not present or found on Spotify.")

#%%
spotify_api.update_token()
# -------------------- Refresh the popularity of all songs ------------------- #
songs_spotify = list(db.songs.find({"spotify_uri":{'$exists':True}}))
n = len(songs_spotify)
i=1
for s in songs_spotify:
    print(f"{i}/{n}")
    # spotify_api.update_token()
    update_spotify = get_song_parameters(id=s["spotify_id"],auth_header=spotify_api.AUTH_HEADER)
    # print(update_spotify)
    if update_spotify!={}:
        temp = db.songs.update_one(
                filter={"_id":s["_id"]},
                update={
                    "$set": {
                        "spotify_popularity":update_spotify["popularity"],
                        "last_update": datetime.datetime.utcnow()
                    }
                }
            )
    i+=1


# --------------------------- Refresh all playlists -------------------------- #
#%%
spotify_api.update_token()
all_playlists = list(db.artist_playlist.find({}))
i=1
for p in all_playlists:
    playlist_id = p["playlist_id"]
    artist_name = p["artist_name"]
    next_page = 1

    spotify_uris = []
    spotify_popularity = []
    discarded_tracks = []
    full_tracklist = []
    while next_page!=None:
        songs = genius.get_artist_songs(id=p["artist_genius_id"],page=next_page,per_page=50,details="minimal")
        if songs == {}:
            pass
        full_tracklist+=songs["songs"]
        for s in songs["songs"]:
            search_song = list(db.songs.find({"genius_id":s["id"]}))
            if len(search_song)!=0:
                if "spotify_uri" in search_song[0].keys():
                    if search_song[0]["spotify_uri"]!=None:
                        spotify_uris.append(search_song[0]["spotify_uri"])
                        spotify_popularity.append(search_song[0]["spotify_popularity"])
            else :
                if not bool(re.match(r".*\*$",s["title"])) or bool(re.match(r".*1H\*$",s["title"])):
                    spotify_api.update_token()
                    spotify_song=search_track(track_name=s["title"],auth_header=spotify_api.AUTH_HEADER,artist_name=s["primary_artist"]["name"])
                    if spotify_song!={}:
                        spotify_uris.append(spotify_song["uri"])
                        spotify_popularity.append(spotify_song["popularity"])

                        song = Songs(genius_id = s["id"], spotify_id = spotify_song["id"],spotify_uri = spotify_song["uri"], apple_music_id = None, song_name = s["title"],
                        primary_artist_name = s["primary_artist"]["name"], genius_song = s, spotify_popularity = spotify_song["popularity"], last_update = datetime.datetime.utcnow())
                        song.save(db["songs"])
                    else : 
                        discarded_tracks.append((s["title"],s["primary_artist"]["name"]))
                        song = Songs(genius_id = s["id"], spotify_id = None,spotify_uri = None, apple_music_id = None, song_name = s["title"],
                        primary_artist_name = s["primary_artist"]["name"], genius_song = s,spotify_popularity=None, last_update = datetime.datetime.utcnow())
                        song.save(db["songs"])
        next_page = songs["next_page"]
    
    # Sort the playlist by decreasing popularity on Spotify
    spotify_uris = [uri for _,uri in sorted(zip(spotify_popularity,spotify_uris),reverse=True)]
    spotify_uris = unique(spotify_uris)

    # Remove the previous tracks in the playlist
    tracks_to_delete = {"tracks": [{"uri":uri} for uri in p["tracks_uris"]]}
    spotify_api.update_token()
    auth_delete = {"Content-Type":"application/json","Authorization":spotify_api.AUTH_HEADER["Authorization"]}
    url_delete = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    if len(tracks_to_delete["tracks"])%100==0:
        n_split = len(tracks_to_delete["tracks"])//100
    else :
        n_split = len(tracks_to_delete["tracks"])//100+1
    for k in range(n_split):
        query = {"tracks":tracks_to_delete["tracks"][k*100:min((k+1)*100,len(tracks_to_delete["tracks"]))]}
        data = json.dumps(query, indent=4)
        r_delete = requests.delete(url_delete,headers=auth_delete,data=data)
        # print(r_delete.status_code)
        if r_delete.status_code not in (200,299):
            print(f"Issue removing the tracks ({r_delete.status_code}) for {artist_name}")

    # Add items to the playlist
    auth_items = {"Content-Type":"application/json","Authorization":spotify_api.AUTH_HEADER["Authorization"]}
    url3 = f"{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks"

    if len(spotify_uris)%100==0:
        n_split = len(spotify_uris)//100
    else :
        n_split = len(spotify_uris)//100+1
    for k in range(n_split):
        query3 = {"uris":spotify_uris[k*100:min((k+1)*100,len(spotify_uris))],"position":100*k}
        data3 = json.dumps(query3, indent=4)
        r3 = requests.post(url3,headers=auth_items,data=data3)
        if r3.status_code not in range(200, 299):
            print("Could not add items to the playlist")
    
    # Modify the playlist in the MongoDB collection
    temp = db.artist_playlist.update_one(
            filter={"_id":p["_id"]},
            update={
                "$set": {
                    "tracks":full_tracklist,
                    "tracks_uris":spotify_uris,
                    "last_update": datetime.datetime.utcnow()
                }
            }
        )
    print(f"Finished updating the playlist for {artist_name} - {i}/{len(all_playlists)}")
    # print(p["playlist_url"])
    i+=1
    

#%%
 
# %%
