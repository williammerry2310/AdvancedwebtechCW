#********************************
#   William Merry
#   Year 3
#   Matric No . 12345
#********************************

from flask import Flask
from pathlib import Path
import sqlite3



# Define the Flask application
app = Flask(__name__)

# Define the database location
DATABASE = Path(__file__).resolve().parent / "Advancedwebtech.db"


# Define the homepage route
@app.route("/")
def home():
    return "<h1>Freshwater Fish Discovery England</h1>"


# Run the Flask application
if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)