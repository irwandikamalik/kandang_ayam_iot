from flask import Flask, render_template, jsonify, request, Response
import mysql.connector
import atexit

from cam import Camera, gen_frames

app = Flask(__name__)

camera = None

current_command = {
    "feed": False,
    "lamp": False,
    "auto" : False,
    "fan": False,
    "mist": False
}

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "iot_user",
    "password": "12345",
    "database": "iot_db"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def get_camera():
    global camera
    if camera is None:
        camera = Camera()
    return camera


@app.route("/")
def index():
    return render_template("index.html")

# DATA SENSOR
@app.route("/data")
def get_data():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT id, suhu, humidity, gas, created_at
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 60
    """

    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(result)

# DATA CONTROL
@app.route('/feed', methods=['POST'])
def feed():
    if not current_command["feed"]:
        current_command["feed"] = True
    return {"status": "ok"}

@app.route('/lamp', methods=['POST'])
def lamp():
    state = request.json['state']
    current_command["lamp"] = state
    return {"status": "ok"}

@app.route('/auto', methods=['POST'])
def auto():
    state = request.json['state']
    current_command["auto"] = state
    return {"status": "ok"}

@app.route('/mist', methods=['POST'])
def mist():
    state = request.json['state']
    current_command["mist"] = state
    return {"status": "ok"}

@app.route('/fan', methods=['POST'])
def fan():
    state = request.json['state']
    current_command["fan"] = state
    return {"status": "ok"}

# DATA SETPOINT
@app.route('/setpoint', methods=['POST'])
def set_setpoint():
    data = request.json

    suhu = float(data['suhu'])
    hum = float(data['hum'])
    gas = float(data['gas'])

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE setpoint
        SET suhu=%s, hum=%s, gas=%s
        WHERE id=1
    """, (suhu, hum, gas))

    db.commit()
    cursor.close()
    db.close()

    return {"status": "ok"}

@app.route('/get-setpoint')
def get_setpoint():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM setpoint WHERE id=1")
    result = cursor.fetchone()

    cursor.close()
    db.close()

    if result:
        return {
        "suhu": result['suhu'],
        "hum": result['hum'],
        "gas": result['gas']
        }   
    
    else:
        return {"suhu": 0, "hum": 0, "gas": 0}

@app.route('/get-command')
def get_command():

    cmd = current_command.copy()

    # reset feed biar cuma sekali trigger
    current_command["feed"] = False

    return cmd

@app.route('/stream')
def stream():
    global camera
    if camera is None:
        camera = Camera()

    return Response(gen_frames(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop-stream')
def stop_stream():
    global camera
    if camera:
        camera.release()
        camera = None
    return {"status": "stopped"}


@atexit.register
def shutdown():
    global camera
    print("🔻 Releasing camera...")
    if camera:
        camera.release()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)