from pathlib import Path
import sqlite3

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "hello_world.db"
SCHEMA = BASE_DIR / "schema.sql"

app = Flask(__name__)


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db_connection() as connection:
        connection.executescript(SCHEMA.read_text(encoding="utf-8"))
        # Add the starter setting the first time the app runs.
        connection.execute(
            "INSERT OR IGNORE INTO settings (id, font_color) VALUES (1, ?)",
            ("#2457C5",),
        )


@app.route("/")
def home():
    with get_db_connection() as connection:
        row = connection.execute(
            "SELECT font_color FROM settings WHERE id = 1"
        ).fetchone()
    return render_template("index.html", font_color=row["font_color"])


@app.route("/api/color", methods=["POST"])
def update_color():
    data = request.get_json(silent=True) or {}
    color = data.get("color", "")

    # Accept only six-digit hex colors, e.g. #2457C5.
    if (
        not isinstance(color, str)
        or len(color) != 7
        or not color.startswith("#")
        or any(character not in "0123456789abcdefABCDEF" for character in color[1:])
    ):
        return jsonify({"error": "Please send a valid hex color."}), 400

    with get_db_connection() as connection:
        connection.execute(
            "UPDATE settings SET font_color = ? WHERE id = 1",
            (color,),
        )

    return jsonify({"font_color": color})


if __name__ == "__main__":
    initialize_database()
    app.run(host="localhost", port=5000, debug=True)
