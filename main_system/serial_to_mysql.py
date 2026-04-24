import serial
import json
import mysql.connector
import time
import sys
import os
import requests

# ================= CONFIG =================
DEBUG = False  # True / False
DEBUG_RESPONSE = False

BAUDRATE = 115200

# AUTO DETECT OS
if sys.platform.startswith("win"):
    DEFAULT_PORT = "COM3"
else:
    DEFAULT_PORT = "/dev/ttyUSB0"

SERIAL_PORT = os.getenv("SERIAL_PORT", DEFAULT_PORT)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "iot_user"),
    "password": os.getenv("DB_PASS", "12345"),
    "database": os.getenv("DB_NAME", "iot_db")
}

# FLASK API (ambil command)
FLASK_URL = "http://127.0.0.1:5000/get-command"
SETPOINT_URL = "http://127.0.0.1:5000/get-setpoint"

# INTERVAL
INTERVAL_DB = 1      # baca sensor
INTERVAL_CMD = 1     # kirim command
# ==========================================

def debug_print(msg):
    if DEBUG:
        print(msg)

def debug_print_respon(msg):
    if DEBUG_RESPONSE:
        print(msg)

# ================= DB =================
def connect_db():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        print("MySQL Connected")
        return db
    except Exception as e:
        print("MySQL Error:", e)
        return None

def insert_data(db, suhu, humidity, gas):
    try:
        cursor = db.cursor()

        query = """
            INSERT INTO sensor_data (suhu, humidity, gas)
            VALUES (%s, %s, %s)
        """

        cursor.execute(query, (suhu, humidity, gas))
        db.commit()
        cursor.close()

        debug_print(f"Insert: {suhu}, {humidity}, {gas}")

    except Exception as e:
        print("Insert Error:", e)

# ================= SERIAL =================
def connect_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"Serial Connected: {SERIAL_PORT}")
        return ser
    except Exception as e:
        print("Serial Error:", e)
        return None

def parse_json(line):
    try:
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    except:
        pass
    return None

# ================= FLASK COMMAND =================
def get_command():
    try:
        res = requests.get(FLASK_URL, timeout=2)
        # debug_print(f"📤 SEND: {res.strip()}")

        return res.json()
    except Exception as e:
        print("❌ Flask Error:", e)
        return None


def send_command(ser, cmd):
    try:
        message = json.dumps(cmd) + "\n"
        ser.write(message.encode())

        debug_print(f"📤 SEND: {message.strip()}")

    except Exception as e:
        print("❌ Send Error:", e)

        try:
            ser.close()
        except:
            pass

        return False
    return True
    
def get_setpoint():
    try:
        res = requests.get(SETPOINT_URL, timeout=2)
        return res.json()
    except Exception as e:
        print("❌ Setpoint Error:", e)
        return None

# ================= MAIN =================
def main():
    ser = connect_serial()
    db = connect_db()

    if not ser or not db:
        print("Gagal start program")
        return

    print("System Running...")

    last_cmd = None
    last_db_time = 0
    last_cmd_time = 0

    while True:
        try:
            now = time.time()

            # ======================
            # CONNECT SERIAL JIKA BELUM
            # ======================
            if ser is None or not ser.is_open:
                print("🔄 Reconnecting serial...")
                try:
                    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
                    time.sleep(2)
                    ser.reset_input_buffer()
                    print("✅ Serial Connected")
                except Exception as e:
                    print("❌ Serial reconnect gagal:", e)
                    time.sleep(2)
                    continue

            # =========================
            # 1. BACA DATA SENSOR
            # =========================
            if ser.in_waiting:
                line = ser.readline().decode(errors='ignore').strip()
                response = ser.readline().decode(errors='ignore').strip()

                if not line:
                    continue

                debug_print(f"RAW: {line}")
                debug_print_respon(f"Respon:  {response}")

                data = parse_json(line)

                if not data:
                    debug_print("Skip non-JSON")
                    continue

                suhu = data.get("suhu")
                humidity = data.get("humidity")
                gas = data.get("gas")

                if suhu is None or humidity is None or gas is None:
                    debug_print("Data tidak lengkap")
                    continue

                insert_data(db, suhu, humidity, gas)

            # =========================
            # 2. KIRIM COMMAND KE ESP32 + SETPOINT KE ESP32
            # =========================
            if now - last_cmd_time >= INTERVAL_CMD:
                last_cmd_time = now

                cmd = get_command()
                sp = get_setpoint()

                if cmd is None or sp is None:
                    continue

                payload = {
                    **cmd,
                    "set_suhu": float(sp["suhu"]),
                    "set_hum": float(sp["hum"]),
                    "set_gas": float(sp["gas"]),
                    "auto": cmd.get("auto", False) 

                }

                debug_print(f"📦 PAYLOAD: {payload}")

                if payload != last_cmd:
                    ok = send_command(ser, payload)

                    if ok:
                        last_cmd = payload
                    else:
                        ser = None


        except Exception as e:
            print("Runtime Error:", e)
            
            try:
                if ser:
                    ser.close()
            except:
                pass

            ser = None
            time.sleep(2)

if __name__ == "__main__":
    main()