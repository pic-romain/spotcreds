import base64, json, requests

from PIL import ImageFont, ImageDraw, Image  
import cv2
import numpy as np  

from urllib.parse import urlencode
import datetime
import re
import unidecode
import pickle

# Automate the authentification
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import urllib.parse as urlparse
from urllib.parse import parse_qs

import genius
from custom_collections import Songs, ArtistPlaylist



# Workaround to support both python 2 & 3
try:
    import urllib.request, urllib.error
    import urllib.parse as urllibparse
except ImportError:
    import urllib as urllibparse


from logs import ERROR_EMAIL
error_email = ERROR_EMAIL()
'''
    --------------------- HOW THIS FILE IS ORGANIZED --------------------

    0. SPOTIFY BASE URLs
    1. CREATING THE IMAGE FOR PLAYLIST
    2. SPOTIFY API CLASS
    3. GET USER INFO
    4. FUNCTIONS TO GET DATA FROM SPOTIFY
    

'''
def load_cookie(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

def unique(liste):
    # initialize a null list
    unique_list = []
    # traverse for all elements
    for x in liste:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list
# ----------------- 0. SPOTIFY BASE URLs ----------------

SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = "v1"
SPOTIFY_API_URL = f"{SPOTIFY_API_BASE_URL}/{API_VERSION}"

# spotify endpoints
SPOTIFY_AUTH_BASE_URL = "https://accounts.spotify.com/{}"
SPOTIFY_AUTH_URL = SPOTIFY_AUTH_BASE_URL.format('authorize')
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL.format('api/token')

# -------------------- 1. CREATING THE IMAGE FOR PLAYLIST -------------------- #

# client keys
CLIENT = json.load(open('conf_spotify.json', 'r'))

def create_playlist_image(artist_name):
    # Colors
    bg_blue = "#070130"
    beige = "#F5E6CF"
    yellow = "#F5ED3B"
    l1 = "Spotlight"
    l2 = "On"

    # Load image in OpenCV  
    image = cv2.imread("data/background.png")  

    # Convert the image to RGB (OpenCV uses BGR)  
    cv2_im_rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

    # Pass the image to PIL  
    pil_im = Image.fromarray(cv2_im_rgb)  

    draw = ImageDraw.Draw(pil_im)  
    # use a truetype font
    font = ImageFont.truetype("data/zilla-slab.regular.ttf", 90)
    font_sb = ImageFont.truetype("data/zilla-slab.semibold.ttf", 80)

    # Positions
    l1_size = font.getsize(l1)
    l1_height = l1_size[1]
    l2_size = font.getsize(l2)
    l2_height = l2_size[1]
    bm=5

    if font_sb.getsize(artist_name)[0]+2*bm>400:
        #Find the fontsize
        fs=80
        while font_sb.getsize(artist_name)[0]+2*bm>400 and fs>40:
            fs-=5
            font_sb = ImageFont.truetype("data/zilla-slab.semibold.ttf", fs)
    elif font_sb.getsize(artist_name)[0]+2*bm<200:
        fs=80
        while font_sb.getsize(artist_name)[0]+2*bm<200 and fs<110:
            fs+=5
            font_sb = ImageFont.truetype("data/zilla-slab.semibold.ttf", fs)

    l3_size = font_sb.getsize(artist_name)
    l3_height = l3_size[1]
    l3_width = l3_size[0]
    vertical_spacing = 10

    bbox = font_sb.getbbox(artist_name)


    (ascent,descent) = font.getmetrics()
    lw = ascent+descent
    (ascent_sb,descent_sb) = font_sb.getmetrics()
    lw_sb = ascent_sb+descent_sb

    left_margin = (500-max(l1_size[0],l3_width+2*bm))/2
    top_margin = (500-(2*lw+lw_sb+2*bm))/2

    draw.text((left_margin, top_margin), l1, font=font,fill=beige) 
    draw.text((left_margin, top_margin+lw-vertical_spacing), l2, font=font,fill=beige)
    draw.rectangle([(left_margin-bm,top_margin+2*lw-vertical_spacing),(left_margin+l3_width+bm,top_margin+2*lw+lw_sb-2*vertical_spacing+2*bm)],fill=yellow) 
    draw.text((left_margin,top_margin+2*(lw-vertical_spacing)+bm+descent_sb/2), artist_name, font=font_sb,fill=bg_blue)

    cv2_im = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
    # Get the image back to OpenCV  
    img_str = cv2.imencode('.jpg',cv2_im)[1].tostring()
    return img_str

# --------------------------- 2. SPOTIFY API CLASS --------------------------- #

class SpotifyAPI(object):
    refresh_token = None
    access_token = None
    access_token_expires_at = datetime.datetime.utcnow()
    access_token_did_expire = True
    CLIENT_ID = None
    CLIENT_SECRET = None
    code = None

    auth_query_parameters = None
    URL_ARGS = None
    AUTH_URL = None
    ACCOUNT_ID = None
    ACCOUNT_PASSWORD = None

    REDIRECT_URI = "https://twitter.com/SpotCredits"
    SCOPE = "ugc-image-upload playlist-modify-public playlist-modify-private"

    CLIENT = json.load(open('conf_spotify.json', 'r'))
    
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = logger
        self.CLIENT_ID = CLIENT['id']
        self.CLIENT_SECRET = CLIENT['secret']
        self.auth_query_parameters = {
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": self.SCOPE,
            "client_id": self.CLIENT_ID
        }
        self.URL_ARGS = "&".join([f"{key}={urllibparse.quote(val)}" for key, val in self.auth_query_parameters.items()])
        self.AUTH_URL = f"{SPOTIFY_AUTH_URL}/?{self.URL_ARGS}"

        spotify_account = json.load(open('conf_spotify_account.json', 'r'))
        self.ACCOUNT_ID = spotify_account["id"]
        self.ACCOUNT_PASSWORD =  spotify_account["password"]

        self.get_code()

        self.update_token()


    def get_code(self):

        # Selenium Firefox
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)
        
        driver.get("https://accounts.spotify.com/404")
        load_cookie(driver=driver,path="data/cookies.txt")
        
        driver.get(self.AUTH_URL)
        # try:
        #     driver.find_element_by_id("login-username").send_keys(self.ACCOUNT_ID)
        #     driver.find_element_by_id ("login-password").send_keys(self.ACCOUNT_PASSWORD)
        #     driver.find_element_by_id("login-button").click()
        # except NoSuchElementException:
        #     print(driver.page_source)
        # try:
        #     auth_button= WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'auth-accept')))
        #     print("Page is ready!")
        #     auth_button.click()
        # except TimeoutException:
        #     print("Loading took too much time!")
        
        url_code = driver.current_url
        parsed_url = urlparse.urlparse(url_code)
        try:
            self.code = parse_qs(parsed_url.query)["code"][0]
        except KeyError :
            self.logger.exception("No code found.")
            self.code = None

        driver.close()
    
    def update_token(self):
        now = datetime.datetime.utcnow()
        self.access_token_did_expire =( self.access_token_expires_at > (now + datetime.timedelta(seconds=20)) )
        
        if self.access_token==None or self.access_token_did_expire:
            self.get_access_token()
        
        return True
        
    def get_access_token(self):
        """
        Returns a base64 encoded string
        """
        if self.CLIENT_SECRET == None or self.CLIENT_ID== None:
            raise Exception("You must set client_id and client_secret")
        base64encoded = base64.b64encode(f"{self.CLIENT_ID}:{self.CLIENT_SECRET}".encode())
        token_headers = {"Authorization": f"Basic {base64encoded.decode()}"}

        if self.refresh_token==None:
            token_data = {
                "grant_type": "authorization_code",
                "code": self.code,
                "redirect_uri": self.REDIRECT_URI
            }
        else :
            token_data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
        post_request = requests.post(SPOTIFY_TOKEN_URL, data=token_data,headers=token_headers)
        if post_request.status_code not in range(200, 299):
            self.logger.exception("Connection refused "+str(post_request.status_code))
            error_email.send(
                subject="Unable to post token",
                content="Connection refused "+str(post_request.status_code)+f"\n Date and Time : {datetime.datetime.now()}")
            raise Exception("Connection refused "+str(post_request.status_code))
            
        
        response_data = json.loads(post_request.text)
        self.access_token = response_data["access_token"]
        if self.refresh_token==None:
            self.refresh_token = response_data["refresh_token"]
        
        self.AUTH_HEADER = {"Authorization": f"Bearer {self.access_token}"}

        # Expiration
        self.access_token_did_expire = False
        now = datetime.datetime.utcnow()
        expires_in = response_data["expires_in"]
        self.access_token_expires_at = now + datetime.timedelta(seconds=expires_in)

    def get_user_information(self):
        url = f"{SPOTIFY_API_URL}/me"
        r = requests.get(url, headers=self.AUTH_HEADER)
        return r.json()
    
    def create_artist_playlist(self, artist_genius_id, artist_name,db):
        user_info = self.get_user_information()
        user_id = user_info["id"]
        # Create the empty playlist
        url1 = f"{SPOTIFY_API_URL}/users/{user_id}/playlists"
        query1 = {
            "name":f"Spotlight On The Credits : {artist_name}",
            "public":"true",
            "description":f"La playlist ultime qui regroupe tous les sons auxquels {artist_name} a contribué."
            }
        data1 = json.dumps(query1, indent=4)
        r1 = requests.post(url1,data=data1,headers=self.AUTH_HEADER)
        if r1.status_code not in range(200, 299):
            self.logger.exception("Connection refused "+str(r1.status_code))
            error_email.send(
                subject="Unable to create playlist",
                content="Connection refused "+str(r1.status_code)+f"\n Artist : {artist_name} \n Date and Time : {datetime.datetime.now()}")
            return False
        playlist_url = r1.json()["external_urls"]["spotify"]

        # Modification of the image
        auth_image = {"Content-Type":"image/jpeg","Authorization":self.AUTH_HEADER["Authorization"]}
        playlist_id = r1.json()["id"]
        
        url2 = f"{SPOTIFY_API_URL}/playlists/{playlist_id}/images"
        
        # Playlist image
        img_str = create_playlist_image(artist_name=artist_name)
        data2 = base64.b64encode(img_str)

        r2 = requests.put(url2,headers=auth_image,data=data2)
        if r2.status_code not in range(200, 299):
            self.logger.exception("Unable to add image to playlist")
            error_email.send(
                subject="Unable to add image to playlist",
                content="Connection refused "+str(r2.status_code)+f"\n Artist : {artist_name} \n Date and Time : {datetime.datetime.now()}")
            return False
        

        next_page = 1
        i = 0
        spotify_uris = []
        spotify_popularity = []
        discarded_tracks = []
        full_tracklist = []
        while next_page!=None:
            songs = genius.get_artist_songs(id=artist_genius_id,page=next_page,per_page=50,details="minimal",logger=self.logger)
            if songs == {}:
                return False
            full_tracklist+=songs["songs"]
            for s in songs["songs"] :
                search_song = list(db.songs.find({"genius_id":s["id"]}))#Songs.objects(genius_id= s["id"])
                if len(search_song)==0:
                    if not bool(re.match(r".*\*$",s["title"])) or bool(re.match(r".*1H\*$",s["title"])):
                        spotify_song=search_track(track_name=s["title"],auth_header=self.AUTH_HEADER,artist_name=s["primary_artist"]["name"])
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
                    else :
                        discarded_tracks.append((s["title"],s["primary_artist"]["name"]))
                        song = Songs(genius_id = s["id"], spotify_id = None,spotify_uri = None, apple_music_id = None, song_name = s["title"],
                        primary_artist_name = s["primary_artist"]["name"], genius_song = s, spotify_popularity=None, last_update = datetime.datetime.utcnow())
                        song.save(db["songs"])
                        
                else :
                    if "spotify_uri" in search_song[0].keys():
                        if search_song[0]["spotify_uri"]!=None:
                            spotify_uris.append(search_song[0]["spotify_uri"])
                            spotify_popularity.append(search_song[0]["spotify_popularity"])
                        else :
                            discarded_tracks.append((search_song[0]["song_name"],search_song[0]["primary_artist_name"]))
                    else :
                        discarded_tracks.append((search_song[0]["song_name"],search_song[0]["primary_artist_name"]))
                        
            next_page = songs["next_page"]
            i=i+1
        
        # Sort the playlist by decreasing popularity on Spotify
        spotify_uris = [uri for _,uri in sorted(zip(spotify_popularity,spotify_uris),reverse=True)]
        spotify_uris = unique(spotify_uris)

        # Add items to the playlist
        auth_items = {"Content-Type":"application/json","Authorization":self.AUTH_HEADER["Authorization"]}
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
                return False
        
        # Save the playlist in the MongoDB collection
        playlist = ArtistPlaylist(
            artist_genius_id = artist_genius_id,
            artist_name = artist_name,
            playlist_id = playlist_id,
            user_id = user_info["id"],
            tracks = full_tracklist,
            tracks_uris = spotify_uris,
            playlist_url = playlist_url,
            last_update = datetime.datetime.utcnow()
            )
        playlist.save(db["artist_playlist"])

        self.logger.info(f"Created and saved playlist for : {artist_name} at {playlist_url} ")
        return playlist_url
    
    def get_playlist_track_uris(self,playlist_id):
        url = f"{SPOTIFY_API_URL}/playlists/{playlist_id}?fields=tracks.items(track(uri))"
        r = requests.get(url, headers=self.AUTH_HEADER)
        print(r.json())
        return r





# ----------------------------- 3. GET USER INFO ----------------------------- #


def get_users_playlists(auth_header):
    url = f"{SPOTIFY_API_URL}/me/playlists"
    r = requests.get(url, headers=auth_header)
    return r.json()

# ------------------- 4. FUNCTIONS TO GET DATA FROM SPOTIFY ------------------ #
def get_playlist(_id, auth_header,limit=20,page=1):
    url = f"{SPOTIFY_API_URL}/playlists/{_id}"
    spotify_playlist = requests.get(url+'?'+urlencode({"fields":",".join(["description",'id',"images","name","owner"])}),headers=auth_header).json()
    spotify_playlist["tracks"] = requests.get(url+'/tracks?'+urlencode({"limit":"20","offset":str((page-1)*limit)}),headers=auth_header).json()
    return spotify_playlist

def get_song_parameters(id,auth_header):
    endpoint = f'{SPOTIFY_API_URL}/tracks/{id}'
    r = requests.get(endpoint,headers=auth_header)
    if r.status_code not in range(200, 299):
        return {}
    r = r.json()
    return(
        {
            "spotify_id":r["id"],
            "title":r["name"],
            "primary_artist":r["artists"][0]["name"],
            "popularity":r["popularity"]
        }
    )
def search_track(track_name,auth_header,artist_name=""):
    # Handling the fact that Genius renames an artist if there are other artists with the same name
    if bool(re.match(r".*\s\([A-Z]{3}\)$",artist_name)):
        artist_name = artist_name[0:(len(artist_name)-6)]
    elif bool(re.match(r".*\)$",artist_name)):
        artist_name = artist_name.split("(")[0]

    
    # Filter Booska-P fresstyles
    if track_name == 'Booska 1H*':
        track_name = "Booska"
    elif "’" in track_name:
        track_name = track_name.replace("’","'")
    
    if "’" in artist_name:
        artist_name = artist_name.replace("’","'")
    

    query = {"track":track_name,"artist":artist_name}
    query_url = " ".join([f"{k}:{v}" for k,v in query.items()])
    endpoint = f"{SPOTIFY_API_URL}/search"+"?"+urlencode({"q":query_url,"type":"track","limit":10})
    
    r = requests.get(endpoint, headers = auth_header)
    if "tracks" in r.json().keys():
        if r.json()["tracks"]["items"]==[] and "(" in track_name:
            track_name = track_name.split("(")[0]
            query = {"track":track_name,"artist":artist_name}
            query_url = " ".join([f"{k}:{v}" for k,v in query.items()])
            endpoint = f"{SPOTIFY_API_URL}/search"+"?"+urlencode({"q":query_url,"type":"track","limit":10})
            r = requests.get(endpoint, headers = auth_header)

    if r.status_code not in range(200, 299):
        return {}
    

    for track in r.json()["tracks"]["items"]:
        track_name_wa = unidecode.unidecode(track_name.lower())
        spotify_name_wa = unidecode.unidecode(track["name"].lower())
        if (spotify_name_wa in track_name_wa or track_name_wa in spotify_name_wa) or track["artists"][0]["name"]==artist_name:
            return(track)
    return {}
    

