#include <DigiCDC.h>
#include <Wire.h>

#define AHT10_ADDR 0x38



void aht10Init() {
  delay(100);
  Wire.beginTransmission(AHT10_ADDR);
  Wire.write(0xE1);
  Wire.write(0x08);
  Wire.write(0x00);
  Wire.endTransmission();
  SerialUSB.refresh();
  SerialUSB.delay(20);
}

bool aht10Read(int16_t *temp10, uint16_t *hum10) {
  Wire.beginTransmission(AHT10_ADDR);
  Wire.write(0xAC);
  Wire.write(0x33);
  Wire.write(0x00);
  Wire.endTransmission();
  SerialUSB.refresh();
  SerialUSB.delay(80);

  Wire.requestFrom(AHT10_ADDR, 6);

  if (Wire.available() < 6)
    return false;

  uint8_t data[6];

  for (uint8_t i = 0; i < 6; i++)
    data[i] = Wire.read();

  if (data[0] & 0x80)
    return false;

  uint32_t rawHum =
    ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | ((uint32_t)data[3] >> 4);

  uint32_t rawTemp =
    (((uint32_t)data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];

  *hum10 = (rawHum * 1000UL) / 1048576UL;
  *temp10 = ((rawTemp * 2000UL) / 1048576UL) - 500;

  return true;
}

unsigned long btr = 9600;

void setup() {
  Wire.begin();
  SerialUSB.begin();
  SerialUSB.delay(100);
  aht10Init();
  pinMode(1, OUTPUT);
}

void loop() {

  int16_t temp10 = 111;
  uint16_t hum10 = 222;

 
  //if (SerialUSB.available()) ;
  if (aht10Read(&temp10, &hum10) && SerialUSB.available()) { 
    
    SerialUSB.read();
    // Formato:
    // temperatura;umidade
    // 25.3;61.7
    //SerialUSB.refresh();
    SerialUSB.print(temp10 / 10);
    //SerialUSB.delay(10);
    SerialUSB.write('.');
    //SerialUSB.delay(10);
    SerialUSB.print(abs(temp10 % 10));
    //SerialUSB.delay(10);
    SerialUSB.write(';');
    SerialUSB.delay(100);    
    //SerialUSB.refresh();
    digitalWrite(1, HIGH);
    SerialUSB.print(hum10 / 10);
    //SerialUSB.delay(10);
    SerialUSB.write('.');
    //SerialUSB.delay(10);
    SerialUSB.println(hum10 % 10);
    //SerialUSB.delay(10);
    //SerialUSB.write('\n');
    SerialUSB.delay(100);
    //SerialUSB.refresh();
    digitalWrite(1, LOW);
  }

  SerialUSB.delay(10);  
  //SerialUSB.refresh();
  //SerialUSB.delay(100);
  
}