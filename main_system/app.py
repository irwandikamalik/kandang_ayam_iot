from flask import Flask, render_template, jsonify, request, Response, send_from_directory
from flask_cors import CORS
from cam import Camera, gen_frames
import os
import mysql.connector
import atexit
import time
import paho.mqtt.client as mqtt
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'iot-dashboard', 'dist')

app = Flask(__name__)
CORS(app)
camera = None

current_command = {
    "feed": False,
    "lamp": False,
    "auto" : False,
    "fan": False,
    "mist": False
}

latest_setpoint = {
    "suhu": 0,
    "hum": 0,
    "gas": 0,
    "last_update": 0
}
latest_status = {}
latest_sensor = {}

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

# MQTT SETUP
MQTT_BROKER = "192.168.100.82"

def on_connect(client, userdata, flags, rc):
    print("MQTT Connected:", rc)
    client.subscribe("iot/sensor")
    client.subscribe("iot/status")
    client.subscribe("iot/setpoint/status")

def on_message(client, userdata, msg):
    global latest_sensor, latest_status, latest_setpoint

    try:
        data = json.loads(msg.payload.decode())
    except:
        print("JSON ERROR")
        return

    if msg.topic == "iot/sensor":
        latest_sensor = data
        latest_sensor["last_update"] = time.time()


        # simpan ke DB
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO sensor_data (suhu, humidity, gas)
            VALUES (%s, %s, %s)
        """, (data["suhu"], data["humidity"], data["gas"]))

        db.commit()
        cursor.close()
        db.close()

    elif msg.topic == "iot/status":
        latest_status = data
        latest_status["last_update"] = time.time()

    elif msg.topic == "iot/setpoint/status":
        latest_setpoint = data
        latest_setpoint["last_update"] = time.time()


mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_start()

@app.route('/')
def serve_vue():
    return send_from_directory(DIST_DIR, 'index.html')
    
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(DIST_DIR, path)

@app.route('/all')
def get_all():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, suhu, humidity, gas, created_at
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 20
    """)

    sensor = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify({
        "sensor": sensor,
        "status": latest_status,
        "realtime": latest_sensor,
        "server_time": time.time()
    })

# DATA SENSOR
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

# DATA CONTROL
@app.route('/feed', methods=['POST'])
def feed():
    mqtt_client.publish("iot/control", json.dumps({
        "feed": True
    }))

    return {"status": "ok"}

@app.route('/feed_reset', methods=['POST'])
def feed_reset():
    current_command["feed"] = False
    return {"status": "ok"}


@app.route('/lamp', methods=['POST'])
def lamp():
    state = request.json['state']

    mqtt_client.publish("iot/control", json.dumps({
        "lamp": state
    }))

    return {"status": "ok"}

@app.route('/auto', methods=['POST'])
def auto():
    state = request.json['state']

    mqtt_client.publish("iot/control", json.dumps({
        "auto": state
    }))

    return {"status": "ok"}

@app.route('/mist', methods=['POST'])
def mist():
    state = request.json['state']

    mqtt_client.publish("iot/control", json.dumps({
        "mist": state
    }))

    return {"status": "ok"}

@app.route('/fan', methods=['POST'])
def fan():
    state = request.json['state']

    mqtt_client.publish("iot/control", json.dumps({
        "fan": state
    }))

    return {"status": "ok"}

@app.route('/drink', methods=['POST'])
def drink():
    state = request.json['state']

    mqtt_client.publish("iot/control", json.dumps({
        "drink": state
    }))

    return {"status": "ok"}


@app.route('/get-status')
def get_status():
    return {
    **latest_status,
    **latest_sensor,
}

@app.route('/get-setpoint')
def get_setpoint():
    return latest_setpoint


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

    latest_setpoint.update({
        "suhu": suhu,
        "hum": hum,
        "gas": gas,
        "last_update": time.time()
    })


    mqtt_client.publish("iot/setpoint", json.dumps({
        "suhu": suhu,
        "hum": hum,
        "gas": gas
    }), retain=True)

    return {"status": "ok"}

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