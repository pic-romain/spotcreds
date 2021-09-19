class ArtistPlaylist:
    def __init__(self,artist_genius_id,artist_name,playlist_id,user_id,playlist_url,last_update,tracks=[],tracks_uris=[],banned_tracks_uris=[]):
        self.data = {
            "artist_genius_id":artist_genius_id,
            "artist_name":artist_name,
            "playlist_id":playlist_id,
            "user_id":user_id,
            "tracks":tracks,
            "tracks_uris":tracks_uris,
            "banned_tracks_uris":banned_tracks_uris,
            "playlist_url":playlist_url,
            "last_update":last_update
        }
    def save(self,collection):
        if collection!=None:
            collection.insert_one(self.data)
            return True
        return False

class Songs:
    def __init__(self,genius_id,song_name,primary_artist_name,last_update,spotify_id=None,spotify_uri=None,apple_music_id=None,spotify_popularity=None,genius_song={}):
        self.data = {
            "genius_id":genius_id,
            "spotify_id":spotify_id,
            "spotify_uri":spotify_uri,
            "apple_music_id":apple_music_id,
            "song_name":song_name,
            "primary_artist_name":primary_artist_name,
            "spotify_popularity":spotify_popularity,
            "genius_song":genius_song,
            "last_update":last_update
        }
    def save(self,collection):
        if collection!=None:
            collection.insert_one(self.data)
            return True
        return False

class UnknownArtists:
    def __init__(self,tweet_id,tweet,artist_name):
        self.data = {
            "tweet_id":tweet_id,
            "tweet":tweet,  
            "artist_name":artist_name
        }
    def save(self,collection):
        if collection!=None:
            collection.insert_one(self.data)
            return True
        return False