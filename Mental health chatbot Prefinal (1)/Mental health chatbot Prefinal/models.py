from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["chatbot_db"]

chat_collection = db["chats"]

def get_chat_history(user_id):
    return list(chat_collection.find({"user_id": user_id}, {"_id": 0, "messages": 1}))
