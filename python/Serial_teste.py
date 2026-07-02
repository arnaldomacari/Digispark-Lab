import serial
import time

PORTA = "/dev/ttyACM0"

ser = serial.Serial()
ser.port = PORTA
ser.baudrate = 115200
ser.timeout = 3

# importante para alguns CDC
ser.dtr = True
ser.rts = True

ser.open()

# limpa lixo inicial
ser.reset_input_buffer()
ser.reset_output_buffer()

# cutuca o DigiCDC
#ser.write(b"\n")
ser.flush()

time.sleep(1)

while True:
  ser.write(b"teste\n")
  time.sleep(1)
  linha = ser.readline()
  print(repr(linha))