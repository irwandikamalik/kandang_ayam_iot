import mysql.connector
import random
import time

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "iot_user",
    "password": "12345",
    "database": "iot_db"
}

def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

def generate_dummy():
    suhu = random.uniform(25, 35)
    humidity = random.uniform(60, 90)
    gas = random.uniform(100, 300)

    return suhu, humidity, gas

def insert_data(db, suhu, humidity, gas):
    cursor = db.cursor()

    query = """
        INSERT INTO sensor_data (suhu, humidity, gas)
        VALUES (%s, %s, %s)
    """

    cursor.execute(query, (suhu, humidity, gas))
    db.commit()
    cursor.close()

def main():
    db = connect_db()
    print("Dummy data running...")

    while True:
        suhu, hum, gas = generate_dummy()

        insert_data(db, suhu, hum, gas)

        print(f"Insert: {suhu:.2f}, {hum:.2f}, {gas:.2f}")

        time.sleep(1)  # 🔥 interval 1 detik

if __name__ == "__main__":
    main()