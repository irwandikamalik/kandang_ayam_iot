import serial
import json
import mysql.connector
import time
import sys
import os

# ================= CONFIG =================
DEBUG = False  # True / False

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
# ==========================================


def debug_print(msg):
    if DEBUG:
        print(msg)


def connect_db():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        print("MySQL Connected")
        return db
    except Exception as e:
        print("MySQL Error:", e)
        return None


def connect_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"Serial Connected: {SERIAL_PORT}")
        return ser
    except Exception as e:
        print("Serial Error:", e)
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


def parse_json(line):
    try:
        if line.startswith("{") and line.endswith("}"):
            return json.loads(line)
    except:
        pass
    return None


def main():
    ser = connect_serial()
    db = connect_db()

    if not ser or not db:
        print("Gagal start program")
        return

    print("System Running...")

    while True:
        try:
            line = ser.readline().decode(errors='ignore').strip()

            if not line:
                continue

            debug_print(f"RAW: {line}")

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

        except Exception as e:
            print("Runtime Error:", e)
            time.sleep(1)


if __name__ == "__main__":
    main()