
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise ValueError("MONGO_URL is missing from .env file")

client = MongoClient(MONGO_URL)

db = client["school_management"]

student_collection = db["students"]
teachers_collection = db["teachers"]
classes_collection = db["classes"]





