from __future__ import print_function
import base64
import json
import requests
import sys
import spotify
from urllib.parse import urlencode


# Workaround to support both python 2 & 3
try:
    import urllib.request, urllib.error
    import urllib.parse as urllibparse
except ImportError:
    import urllib as urllibpars

'''
    --------------------- HOW THIS FILE IS ORGANIZED --------------------

    0. GENIUS BASE URL
    1. USER AUTHORIZATION


'''

# ---------------------------- 0. GENIUS BASE URL ---------------------------- #

GENIUS_API_BASE_URL = 'https://api.genius.com'
GENIUS_API_URL = f"{GENIUS_API_BASE_URL}"

# ----------------------------- 1. GET CLIENT IDs ---------------------------- #

CLIENT = json.load(open('conf_genius.json', 'r'))
CLIENT_ID = CLIENT['id']
CLIENT_SECRET = CLIENT['secret']
ACCESS_TOKEN = CLIENT['access_token']

auth_headers = {
    "Authorization":f"Bearer {ACCESS_TOKEN}"
}

# ---------------------------- 2. GET BASE OBJECTS --------------------------- #

def get_artist(id):
    endpoint = f'{GENIUS_API_URL}/artists/{id}'
    r=requests.get(endpoint, headers=auth_headers)
    if r.status_code not in range(200,299):
        return({})
    return r.json()

def get_song(id):
    endpoint = f'{GENIUS_API_URL}/songs/{id}'
    r=requests.get(endpoint, headers=auth_headers)
    if r.status_code not in range(200,299):
        return({})
    return r.json()


# ------------------------ 3. GET MORE COMPLEX OBJECTS ----------------------- #

def get_artist_songs(id,page=1,per_page=20, details = 'all'):
    endpoint = f'{GENIUS_API_URL}/artists/{id}/songs?'+urlencode({"page":page,'per_page':per_page,'sort':'popularity'})
    r=requests.get(endpoint, headers=auth_headers)
    if r.status_code not in range(200,299):
        return({})
    if details == "all":
        songs_extended = []
        for song in r.json()["response"]["songs"]:
            songs_extended.append(get_song(song["id"])["response"]["song"])
        return {'songs':songs_extended,"next_page":r.json()["response"]["next_page"]}
    elif details == "minimal":
        return r.json()["response"]


# ------------------------- 4. SEARCH GENIUS DATABASE ------------------------ #
def get_song(id):
    endpoint = f'{GENIUS_API_URL}/songs/{id}'
    r=requests.get(endpoint, headers=auth_headers)
    if r.status_code not in range(200,299):
        return({})
    return r.json()   
    
def search_track(query, per_page=5):
    endpoint = f'{GENIUS_API_URL}/search?'+urlencode({'q':query,"per_page":per_page})
    r=requests.get(endpoint, headers=auth_headers)
    if r.status_code not in range(200,299):
        return({})
    return r.json()

def unique_artists(list_artists):
    r = []
    r_id = []
    for a in list_artists:
        if not a["id"] in r_id:
            r.append(a)
            r_id.append(a["id"])
        else :
            i = r_id.index(a["id"])
            if not a["found_as"][0] in r[i]['found_as']:
                r[i]["found_as"].append(a["found_as"][0])
    return r

def search_artist(query,per_page = 5, page=1):
    endpoint = f'https://api.genius.com/search?'+urlencode({'q':query})#,"per_page":per_page,"page":page
    r=requests.get(endpoint, headers=auth_headers)
    results = []

    if r.status_code not in range(200,299):
        return([])
    
    # If we find the artist as a primary artist
    for s in r.json()['response']['hits']:
        if s['result']['primary_artist']['name'].lower()==query.lower():
            results.append({"name":s['result']['primary_artist']['name'],
                            'id':s['result']['primary_artist']['id'],
                            'image':s['result']['primary_artist']['image_url'],
                            "genius_url":s['result']['primary_artist']['url'],
                            "found_as":["main_artist"]})
            return(unique_artists(results))
    # Otherwise, we look in the producers
    songs_id = [s['result']['id'] for s in r.json()['response']['hits']]
    for s_id in songs_id:
        producers = [(p["name"],p["id"],p["image_url"],p["url"]) for p in get_song(s_id)['response']["song"]["producer_artists"] if get_song(s_id)['response']["song"]["producer_artists"]!=[]]
        for p in producers:
            if p[0].lower()==query.lower():
                results.append({"name":p[0],
                                'id':p[1],
                                'image':p[2],
                                "genius_url":p[3],
                                "found_as":["producer"]})
    return(unique_artists(results))


def get_song_artists(spotify_id,auth_header):
    spotify_parameters = spotify.get_song_parameters(spotify_id,auth_header)
    query=spotify_parameters["primary_artist"]+" "+spotify_parameters["title"]
    r0 = search_track(query)["response"]['hits']

    genius_parameters = spotify_parameters.copy()
    genius_parameters["producers"] = []

    if len(r0)!=0:
        r1 = r0[0]
        genius_parameters["genius_id"] = r1["result"]["id"]
        r2 = get_song(r1["result"]["id"])
        genius_parameters["primary_artist"] = {"id":r2['response']["song"]["primary_artist"]['id'],
                                                "name":r2['response']["song"]["primary_artist"]["name"],
                                                "genius_profile":r2['response']["song"]["primary_artist"]["url"]
                                              }
        genius_parameters["featured_artists"] = r2["response"]["song"]["featured_artists"].copy()

        for p in r2['response']["song"]["producer_artists"]:
            genius_parameters["producers"].append(
                                                {"id":p['id'],
                                                "name":p["name"],
                                                "genius_profile":p['url']}
                                                )
        return genius_parameters
    genius_parameters["genius_id"] = None
    return genius_parameters