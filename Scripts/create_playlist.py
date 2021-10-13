
import json

from spotify import SpotifyAPI
import genius
from twitter import auth_twitter, read_last_seen, write_last_seen

import pymongo
from custom_collections import UnknownArtists


import logging, datetime
from logs import mkdir_p, ERROR_EMAIL
import os

log_filename = f"logs/create_playlist/{datetime.date.today()}.log"
mkdir_p(os.path.dirname(log_filename))

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
file_handler = logging.FileHandler(filename=log_filename)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


if __name__ == "__main__":
    
    artist_input = input("Artist to add :")
    artists_toadd = artist_input.split(",")
    # Connecting to the db
    db_name = "dbspotcred"
    # Set client
    client = pymongo.MongoClient(
        host='localhost:27017'
    )
    db = client.dbspotcred

    # Get the APIs keys 
    spotify_account = json.load(open('conf_spotify_account.json', 'r'))
    spotify_api = SpotifyAPI(logger=logger)


    artistsRequested = []
    
    for a in artists_toadd:
        query = a
        
        res = genius.search_artist(query=query,logger=logger)
        if len(res)==0:
            logger.info(f'{a} was not found')

        else :
            artist = res[0]
            search_playlist = list(db.artist_playlist.find({"artist_genius_id":artist["id"]}))
            if len(search_playlist)!=0:
                logger.info("On a trouvé et vite en plus ! En même temps, on l'avait déjà créée cette playlist : "+search_playlist[0]["playlist_url"]+" Bonne écoute !")

            else :
                logger.info(f" On a bien trouvé {query} sur Genius. En attendant que je te concocte ta playlist, tu peux visiter son profil Genius : " + artist["genius_url"])
                
                created_playlist = spotify_api.create_artist_playlist(artist_genius_id=artist["id"],artist_name=artist["name"],db=db)#logger=#logger,)
                if created_playlist==False:


                    logger.info("Created : False ")
                        
                else :
                    logger.info("C'est bon ! Tu peux retrouver cette playlist sur notre profil Spotify : " + created_playlist)


        
    if len(artists_toadd)!=0:
        logger.info("J'ai fini. Je repars dormir...")
    else:
        logger.info("Rien de neuf. Je retourne me pieuter...")


