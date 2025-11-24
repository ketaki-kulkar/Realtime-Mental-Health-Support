import nltk
import numpy as np
from keras.models import load_model
import pickle
import random
import json
import re

# Load resources
model = load_model("./model.h5")
words = pickle.load(open("./texts.pkl", "rb"))
classes = pickle.load(open("./labels.pkl", "rb"))

# NLTK setup
lemmatizer = nltk.WordNetLemmatizer()

def clean_sentence(sentence):
    tokens = nltk.word_tokenize(sentence)
    tokens = [lemmatizer.lemmatize(w.lower()) for w in tokens]
    return tokens

def bag_of_words(sentence, words):
    sentence_tokens = clean_sentence(sentence)
    bag = [1 if w in sentence_tokens else 0 for w in words]
    return np.array(bag)

def predict_intent(sentence):
    bow = bag_of_words(sentence, words)

    res = model.predict(np.array([bow]))[0]
    threshold = 0.5
    results = [[i, r] for i, r in enumerate(res) if r > threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return [(classes[r[0]], str(r[1])) for r in results]

def get_response(intent, intents):
    for intent_data in intents["intents"]:
        if intent_data["tag"] == intent:
            return random.choice(intent_data["responses"])
    return "I'm sorry, I couldn't understand. Can you rephrase that?"


def extract_response(raw_response):
    try:
        # Match only the strict JSON format {"response": "value"}
        match = re.search(r'{"response":\s*"([^"]+)"}', raw_response)
        if match:
            return match.group(1)  # Extract the value of the 'response' key
        return "I couldn't understand."
    except Exception as e:
        print(f"Error parsing response: {e}")
        return "I couldn't understand."