from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

print("✅ .env loaded from:", env_path)

MONGO_URI = os.getenv("MONGO_URI")
print("🔍 URI:", MONGO_URI)

if not MONGO_URI:
    print("❌ MONGO_URI not found. Check your .env file.")
    exit()

try:
    client = MongoClient(MONGO_URI)
    db = client["test"]               # Your DB name
    collection = db["blogs"]                # Your Collection name

    test_doc = {"title": "Mongo Test", "msg": "Hello from Python"}
    result = collection.insert_one(test_doc)
    print("✅ Test document inserted with ID:", result.inserted_id)

except Exception as e:
    print("❌ MongoDB connection failed:", str(e))
