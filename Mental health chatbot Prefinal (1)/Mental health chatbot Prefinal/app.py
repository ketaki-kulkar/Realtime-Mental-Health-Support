from flask import Flask, session
from routes import main
from auth_routes import auth
from datetime import timedelta
import os
import google.generativeai as genai

app = Flask(__name__)

# Secret key for user session
app.secret_key = 'mental-bot'
genai.configure(api_key="AIzaSyCMUunexNh6gqxuAtXkFDFBhO4euMowK5M") # Replace with your API key
model = genai.GenerativeModel('gemini-pro') # Or 'gemini-pro-vision'
# Set session lifetime (optional)
app.permanent_session_lifetime = timedelta(minutes=10)

# Register blueprints
app.register_blueprint(main)
app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(debug=True)
