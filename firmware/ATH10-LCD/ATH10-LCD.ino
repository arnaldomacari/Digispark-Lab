#include <DigisparkOLED.h>
#include <Wire.h>

#define AHT10_ADDR 0x38

void aht10Init() {
  delay(100);

  Wire.beginTransmission(AHT10_ADDR);
  Wire.write(0xE1);
  Wire.write(0x08);
  Wire.write(0x00);
  Wire.endTransmission();

  delay(20);
}

bool aht10Read(int16_t *temp10, uint16_t *hum10) {
  Wire.beginTransmission(AHT10_ADDR);
  Wire.write(0xAC);
  Wire.write(0x33);
  Wire.write(0x00);
  Wire.endTransmission();

  delay(80);

  Wire.requestFrom(AHT10_ADDR, 6);

  if (Wire.available() < 6) {
    return false;
  }

  uint8_t data[6];

  for (uint8_t i = 0; i < 6; i++) {
    data[i] = Wire.read();
  }

  if (data[0] & 0x80) {
    return false;
  }

  uint32_t rawHum = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | ((uint32_t)data[3] >> 4);

  uint32_t rawTemp = (((uint32_t)data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];

  *hum10 = (rawHum * 1000UL) / 1048576UL;
  *temp10 = ((rawTemp * 2000UL) / 1048576UL) - 500;

  return true;
}

void printDecimal10(int value) {
  if (value < 0) {
    oled.print("-");
    value = -value;
  }

  oled.print(value / 10);
  oled.print(".");
  oled.print(value % 10);
}


void oledNormal() {
  oled.ssd1306_send_command(0xA0);  // segment remap normal
  oled.ssd1306_send_command(0xC0);  // COM scan normal
}

void setup() {
  Wire.begin();
  oled.begin();
  oled.clear();
  oledNormal();

  oled.setFont(FONT8X16);
  oled.setCursor(0, 0);
  oled.print(F("Digispark LAB"));

  aht10Init();
  delay(1000);
}


void loop() {
  int16_t temp10;
  uint16_t hum10;

  if (aht10Read(&temp10, &hum10)) {
    oled.setFont(FONT8X16);

    oled.setCursor(0, 2);
    oled.print(F("T: "));
    printDecimal10(temp10);
    oled.print(F(" C "));


    oled.setCursor(0, 4);
    oled.print(F("H: "));
    printDecimal10(hum10);
    oled.print(F(" % "));

  } else {
    oled.setFont(FONT8X16);
    oled.setCursor(0, 0);
    oled.print(F("AHT10"));

    oled.setCursor(0, 2);
    oled.print(F("ERRO I2C"));
  }

  delay(2000);
}
