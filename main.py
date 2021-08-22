import json

from spotify import SpotifyAPI
import genius
from twitter import auth_twitter, read_last_seen, write_last_seen

import pymongo
from custom_collections import UnknownArtists

import re
import time

# Connecting to the db
db_name = "dbspotcred"
# Set client
client = pymongo.MongoClient(
    host='localhost:27017'
)
db = client.dbspotcred

# Get the APIs keys 
spotify_account = json.load(open('conf_spotify_account.json', 'r'))
TWITTER_CLIENT = json.load(open('conf_twitter.json', 'r'))

if __name__ == "__main__":
    spotify_api = SpotifyAPI()
    twitter_api = auth_twitter(twitter_client=TWITTER_CLIENT)


    artistsRequested = []
    tweets = twitter_api.mentions_timeline(
        read_last_seen("last_seen.txt"),
        tweet_mode='extended')
    tweets = tweets[::-1]
    for t in tweets:
        m = re.search(r"playlist\s\S*\s(.*)\sstp",t.full_text)
        if bool(m) and t.user.screen_name!="SpotCredits":
            
            related_tweets = []
            query = m.group(1)
            artistsRequested.append(query)
            starting_tweet = twitter_api.update_status("@"+t.user.screen_name + f" Très bien, je vais essayer de créer une playlist pour {query} !",t.id)
            related_tweets.append(starting_tweet.id)
            res = genius.search_artist(query=query)
            if len(res)==0:
                unknown_tweet = twitter_api.update_status("@"+t.user.screen_name + f" Les gars et moi, on a rien trouvé. Alors soit c'est toi qui a merdé, soit c'est nous qui sommes pas assez doué encore... Si tu penses que ça vient de nous, tu peux informer notre chef @pic_romain.",starting_tweet.id)
                unknown_artist = UnknownArtists(
                    tweet_id = t.id,
                    tweet = t._json,
                    artist_name = query
                )
                unknown_artist.save(db["unknown_artist"])

            else :
                artist = res[0]
                search_playlist = list(db.artist_playlist.find({"artist_genius_id":artist["id"]}))
                if len(search_playlist)!=0:
                    already_generated_tweet = twitter_api.update_status("@"+t.user.screen_name + " On a trouvé et vite en plus ! En même temps, on l'avait déjà créée cette playlist : "+search_playlist[0]["playlist_url"]+" Bonne écoute !",starting_tweet.id)

                else :

                    waiting_tweet = twitter_api.update_status("@"+t.user.screen_name + f" On a bien trouvé {query} sur Genius. En attendant que je te concocte ta playlist, tu peux visiter son profil Genius : " + artist["genius_url"],starting_tweet.id)
                    
                    created_playlist = spotify_api.create_artist_playlist(artist_genius_id=artist["id"],artist_name=artist["name"],db=db)#logger=#logger,)
                    if created_playlist==False:


                        #Delete tweets
                        for _id in related_tweets:
                            twitter_api.destroy_status(_id)
                            
                    else :
                        freshly_created_tweet = twitter_api.update_status("@"+t.user.screen_name + " C'est bon ! Tu peux retrouver cette playlist sur notre profil Spotify : " + created_playlist, waiting_tweet.id)


        
    if len(tweets)!=0:
        write_last_seen("last_seen.txt",tweets[-1].id)
        print("Je repars dormir...")

    else:
        print("Rien de neuf. Je retourne me pieuter...")


