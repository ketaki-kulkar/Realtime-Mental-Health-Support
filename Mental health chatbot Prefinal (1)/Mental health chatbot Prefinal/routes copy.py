from flask import Blueprint, request, jsonify, render_template
import json
import pickle
import numpy as np
import nltk
from keras.models import load_model
from langchain_community.llms import GPT4All
from langchain_core.prompts import PromptTemplate
from nltk.stem import WordNetLemmatizer
import re

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
nltk.download("punkt")
nltk.download("wordnet")

def classify_intent(sentence):
    """Classify the intent of a user message."""
    try:
        tokens = nltk.word_tokenize(sentence)
        tokens = [lemmatizer.lemmatize(word.lower()) for word in tokens]
        bag = np.array([1 if word in tokens else 0 for word in words])
        res = model.predict(np.array([bag]))[0]
        confidence_threshold = 0.7
        if max(res) > confidence_threshold:
            return classes[np.argmax(res)]
        return None
    except Exception as e:
        print(f"Error classifying intent: {e}")
        return None

# Routes
@main.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")

@main.route("/get_response", methods=["GET", "POST"])
def get_response_api():
    """Handle user queries."""
    try:
        # Get user message
        user_message = (
            request.get_json().get("message") if request.method == "POST" else request.args.get("message")
        )
        if not user_message:
            return jsonify({"response": "Please provide a valid message."})

        print(f"Received message: {user_message}")

        # Classify intent
        intent = classify_intent(user_message)

            # Get response from intents
        for i in intents["intents"]:
            if i["tag"] == intent:
                response = np.random.choice(i["responses"])
                break

            else:
                response = "Please go on. Will try to reply you"
        
        print(f"Response: {response}")
        return jsonify({"response": response})

    except Exception as e:
        print(f"Error in get_response_api: {e}")
        return jsonify({"error": "An internal error occurred"}), 500
