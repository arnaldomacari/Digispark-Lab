import serial
import time

ser = serial.Serial("/dev/ttyACM1", 9600, timeout=2)

time.sleep(2)

while True:
    ser.write(b"\n")
    linha = ser.readline().decode("utf-8", errors="ignore").strip()
    if linha:
        print(linha)
    time.sleep(2)