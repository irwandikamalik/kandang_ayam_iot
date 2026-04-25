import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import os

# =========================
# 🔧 CONFIG
# =========================
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "iot_user",
    "password": "12345",
    "database": "iot_db"
}

TABLE_NAME = "sensor_data"
FOLDER_NAME = "log_sensor"

# =========================
# 📁 BUAT FOLDER JIKA BELUM ADA
# =========================
if not os.path.exists(FOLDER_NAME):
    os.makedirs(FOLDER_NAME)
    print(f"📁 Folder '{FOLDER_NAME}' dibuat")

# =========================
# 📅 AMBIL TANGGAL KEMARIN
# =========================
yesterday = datetime.now() - timedelta(days=1)
date_str = yesterday.strftime('%Y-%m-%d')

print("📆 Backup data tanggal:", date_str)

# =========================
# 🔌 CONNECT MYSQL
# =========================
db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor(dictionary=True)

# =========================
# 1. AMBIL DATA
# =========================
query = f"""
SELECT * FROM {TABLE_NAME}
WHERE DATE(created_at) = %s
"""

cursor.execute(query, (date_str,))
rows = cursor.fetchall()

if not rows:
    print("⚠️ Tidak ada data untuk tanggal ini")
    cursor.close()
    db.close()
    exit()

# =========================
# 2. SIMPAN KE CSV
# =========================
df = pd.DataFrame(rows)

filename = f"{FOLDER_NAME}/backup_{date_str}.csv"
df.to_csv(filename, index=False)

print(f"✅ Data berhasil disimpan ke: {filename}")

# =========================
# 3. VALIDASI (ANTI KEHAPUS KOSONG)
# =========================
if len(rows) < 10:
    print("⚠️ Data terlalu sedikit, skip delete untuk keamanan")
    cursor.close()
    db.close()
    exit()

# =========================
# 4. HAPUS DATA MYSQL
# =========================
delete_query = f"""
DELETE FROM {TABLE_NAME}
WHERE DATE(created_at) = %s
"""

cursor.execute(delete_query, (date_str,))
db.commit()

print("🔥 Data lama berhasil dihapus dari MySQL")

# =========================
# 🔚 CLOSE
# =========================
cursor.close()
db.close()

print("🚀 SELESAI")