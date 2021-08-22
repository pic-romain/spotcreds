
import sys
sys.path.insert(0, 'C:\\Users\\rpic\\Documents\\spotcreds')


import json

from spotify import SpotifyAPI
import genius
from twitter import auth_twitter, read_last_seen, write_last_seen

import pymongo
from custom_collections import UnknownArtists

import re



if __name__ == "__main__":

    artists_toadd = ["Scar Productions", "La Miellerie"]

    # Connecting to the db
    db_name = "dbspotcred"
    # Set client
    client = pymongo.MongoClient(
        host='localhost:27017'
    )
    db = client.dbspotcred

    # Get the APIs keys 
    spotify_account = json.load(open('conf_spotify_account.json', 'r'))
    spotify_api = SpotifyAPI()


    artistsRequested = []
    
    for a in artists_toadd:
        query = a
        
        res = genius.search_artist(query=query)
        if len(res)==0:
            print(f'{a} was not found')

        else :
            artist = res[0]
            search_playlist = list(db.artist_playlist.find({"artist_genius_id":artist["id"]}))
            if len(search_playlist)!=0:
                print("On a trouvé et vite en plus ! En même temps, on l'avait déjà créée cette playlist : "+search_playlist[0]["playlist_url"]+" Bonne écoute !")

            else :
                print(f" On a bien trouvé {query} sur Genius. En attendant que je te concocte ta playlist, tu peux visiter son profil Genius : " + artist["genius_url"])
                
                created_playlist = spotify_api.create_artist_playlist(artist_genius_id=artist["id"],artist_name=artist["name"],db=db)#logger=#logger,)
                if created_playlist==False:


                    print("Created : False ")
                        
                else :
                    print("C'est bon ! Tu peux retrouver cette playlist sur notre profil Spotify : " + created_playlist)


        
    if len(artists_toadd)!=0:
        print("J'ai fini. Je repars dormir...")
    else:
        print("Rien de neuf. Je retourne me pieuter...")


