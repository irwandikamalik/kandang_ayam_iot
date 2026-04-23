import subprocess
import sys

print("Menjalankan app.py...")
result1 = subprocess.run([sys.executable, "app.py"])

if result1.returncode != 0:
    print("app.py gagal dijalankan")
    exit()

print("Menjalankan serial_to_mysql.py...")
result2 = subprocess.run([sys.executable, "serial_to_mysql.py"])