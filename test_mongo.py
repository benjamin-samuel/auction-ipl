from pymongo import MongoClient

MONGO_URI = "mongodb+srv://benjosamuvel_db_user:vBLiptWSZqMh12f7@cluster1.ae0z7nx.mongodb.net/?appName=Cluster1"

client = MongoClient(MONGO_URI)
db = client["auction_db"]
print(db.list_collection_names())
