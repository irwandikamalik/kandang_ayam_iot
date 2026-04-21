import serial
import time
import requests
import sys

# ================= CONFIG =================
FLASK_URL = "http://127.0.0.1:5000/get-command"
BAUDRATE = 115200

# AUTO DETECT PORT
if sys.platform.startswith("win"):
    SERIAL_PORT = "COM3"
else:
    SERIAL_PORT = "/dev/ttyUSB0"

INTERVAL = 1  # detik
# ==========================================


def connect_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"✅ Serial Connected: {SERIAL_PORT}")
        time.sleep(2)  # tunggu ESP siap
        return ser
    except Exception as e:
        print("❌ Serial Error:", e)
        return None


def get_command():
    try:
        res = requests.get(FLASK_URL, timeout=2)
        return res.json()
    except Exception as e:
        print("❌ Flask Error:", e)
        return None


def send_to_esp32(ser, data):
    try:
        # kirim JSON string
        message = str(data) + "\n"
        ser.write(message.encode())
        print("📤 Sent:", message.strip())
    except Exception as e:
        print("❌ Send Error:", e)


def main():
    ser = connect_serial()

    if not ser:
        print("Gagal start program")
        return

    print("🚀 Bridge Running...")

    last_data = None

    while True:
        try:
            cmd = get_command()

            if not cmd:
                time.sleep(INTERVAL)
                continue

            # biar gak spam kirim terus
            if cmd != last_data:
                send_to_esp32(ser, cmd)
                last_data = cmd

            time.sleep(INTERVAL)

        except Exception as e:
            print("❌ Runtime Error:", e)
            time.sleep(2)


if __name__ == "__main__":
    main()