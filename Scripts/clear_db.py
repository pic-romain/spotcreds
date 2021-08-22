#%%

import pymongo
import json
db_name = "dbspotcred"
mongodb_creds = json.load(open('../conf_mongodb.json', 'r'))
# Set client
client = pymongo.MongoClient(
    host=f'mongodb://{mongodb_creds["id"]}:{mongodb_creds["password"]}@13.37.86.164:27017/?authSource={db_name}'
)
db = client.dbspotcred

print(db.artist_playlist.delete_one({"artist_name":"Meryl"}))
# %%
