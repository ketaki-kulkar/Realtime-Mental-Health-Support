from flask import Blueprint, request, jsonify, render_template, session
import json
import pickle
import numpy as np
import nltk
import mysql.connector
import re
import markdown
from datetime import datetime
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import google.generativeai as genai

import os



# Blueprint setup
main = Blueprint("main", __name__)

# Load model and resources
model = load_model("model.h5")
words = pickle.load(open("texts.pkl", "rb"))
classes = pickle.load(open("labels.pkl", "rb"))

# Load intents
with open("intents.json", "r") as f:
    intents = json.load(f)

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()
nltk.download('punkt_tab')
nltk.download("punkt")
nltk.download("wordnet")

# Initialize Gemini API 
genai.configure(api_key="AIzaSyCMUunexNh6gqxuAtXkFDFBhO4euMowK5M") 
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

# MySQL Database connection settings
DB_HOST = 'localhost'  # Change to your MySQL host
DB_USER = 'root'       # Your MySQL username
DB_PASSWORD = ''  # Your MySQL password
DB_NAME = 'mental_health_chatbot'  # The database name

def generate_gemini_response(user_message):
    """Generate a response using Gemini API."""
    try:
        #response = gemini_model.generate_content(user_message)
        #return response.text
        response = gemini_model.generate_content(user_message)
        markdown_text = response.text
        html_output = markdown.markdown(markdown_text)
        # Then display html_output in your web page
        return html_output
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return "Sorry, I couldn't process your request."

# Classify intent
def classify_intent(sentence):
    """Predict user intent based on trained model."""
    tokens = nltk.word_tokenize(sentence)
    tokens = [lemmatizer.lemmatize(word.lower()) for word in tokens]
    bag = np.array([1 if word in tokens else 0 for word in words])
    
    res = model.predict(np.array([bag]))[0]
    confidence_threshold = 0.7
    return classes[np.argmax(res)] if max(res) > confidence_threshold else None

# Store chat history in MySQL
def store_chat(user_id, user_message, bot_response):
    """Store chat conversations in MySQL."""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='mental_health_chatbot'
        )

        cursor = conn.cursor()

        query = """
            INSERT INTO chat_history (user_id, user_message, bot_response) 
            VALUES (%s, %s, %s)
        """
        
        if isinstance(bot_response, np.str_):
            bot_response = str(bot_response)

        print(f"Executing query: {query} with parameters: {(user_id, user_message, bot_response)}")

        cursor.execute(query,(user_id, user_message, bot_response))
        
        conn.commit()
        conn.close()

    except mysql.connector.IntegrityError as e:
        print("Integrity Error:", e)  # Handle foreign key, unique constraint violations
        conn.rollback()
    except mysql.connector.DataError as e:
        print("Data Error:", e)  # Handle data type mismatches
        conn.rollback()
    except mysql.connector.Error as e:
        print("General Error:", e)  # Handle other errors
        conn.rollback()

# Retrieve chat history
def get_chat_history(user_id):
    """Retrieve chat history for a given user."""
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_message, bot_response, timestamp 
        FROM chat_history 
        WHERE user_id = %s 
        ORDER BY timestamp ASC
    """, (user_id,))
    chats = cursor.fetchall()
    conn.close()
    return chats

# Routes
@main.route("/")
def home():
    """Render the chat page with user's chat history."""
    user_id = session.get("userId")
    if not user_id:
        user_id = None
        
    print(f"Current user: {user_id}")
    return render_template("index.html")

@main.route("/get_response", methods=["POST"])
def get_response_api():
    """Handle user queries, generate responses, and store chat history."""
    try:
        user_message = request.get_json().get("message")
        print(session)
        user_id = session.get("userId")
        if not user_id:
            user_id = None

        print(f"Received message from {user_id}: {user_message}")

        # Check for greetings
        greetings = {"hi", "hello", "hey", "greetings"}
        if user_message.lower() in greetings:
            response = "Hello! How can I assist you today?"
        else:
            intent = classify_intent(user_message)

            response = (np.random.choice([i["responses"] for i in intents["intents"] if i["tag"] == intent][0])
                        if intent else generate_gemini_response(user_message))

        if "Sorry, I couldn't process your request." in response:
            response = generate_gemini_response(user_message)
        print(f"Generated response: {response}")

        # Store chat history in MySQL
        store_chat(user_id, user_message, response)

        return jsonify({"response": response})

    except Exception as e:
        print(f"Error in get_response_api: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

@main.route("/chat_history", methods=["GET"])
def chat_history():
    try:
        user_id = session.get("userId", "guest")

        response = get_chat_history(user_id)

        return jsonify({"response": response})

    except Exception as e:
        print(f"Error in chat_history: {e}")
        return jsonify({"error": "An internal error occurred"}), 500