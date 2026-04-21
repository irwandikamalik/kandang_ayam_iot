from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "iot_user",
    "password": "12345",
    "database": "iot_db"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT id, suhu, humidity, gas, created_at
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 20
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)