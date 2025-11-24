1.	Create and Activate a Virtual Environment (optional but recommended) Open a terminal (Command Prompt, PowerShell, or a terminal in VS Code) and run the following commands inside the copied project folder:
o	On macOS/Linux:
o	python3 -m venv venv
source venv/bin/activate
o	On Windows:
o	python -m venv venv
venv\Scripts\activate
2.	Install Dependencies
pip install -r requirements.txt
The requirements.txt includes the following packages:
o	Flask
o	keras
o	nltk
o	numpy
o	spacy
o	spacy-langdetect
o	spacy-legacy
o	spacy-loggers
o	transformers
o	sentencepiece
o	sacremoses
o	torch
o	torchvision
o	torchaudio
3.	Download Required NLP Models Some packages like nltk and spacy require model downloads:
import nltk
nltk.download('punkt')
4.	Start MySQL Server Using XAMPP
o	Open the XAMPP Control Panel.
o	Start the MySQL module by clicking the Start button next to it.
o	Optionally, start Apache if your project also uses it.
5.	Connect MySQL to Python Ensure that mysql-connector-python is installed:
pip install mysql-connector-python
Then, your Python code should include something like this to connect:
import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="your_mysql_username",
    password="your_mysql_password",
    database="your_database_name"
)
6.	Run the Flask Application Make sure the main Flask file (e.g., app.py) is in your root directory, then run:
python app.py
