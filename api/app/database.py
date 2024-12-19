# app/database.py
from pymongo import MongoClient
from app.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.api
users_collection = db.users
collection = db.apis  # Access the 'apis' collection within the 'api' database
apis_collection = db.api_requests  # Access the 'api_requests' collection within the 'api' database
