#include <DigisparkOLED.h>
#include <Wire.h>

void oledNormal() {
  oled.ssd1306_send_command(0xA0); // segment remap normal
  oled.ssd1306_send_command(0xC0); // COM scan normal
}

void oledFlip180() {
  oled.ssd1306_send_command(0xA1); // segment remap invertido
  oled.ssd1306_send_command(0xC8); // COM scan invertido
}

void oledContrast(uint8_t value)
{
    oled.ssd1306_send_command(0x81);   // Set Contrast
    oled.ssd1306_send_command(value);  // 0x00 a 0xFF
}

void setup() {
  oled.begin();
  oledNormal(); // ou este, se ficar invertido
  oledContrast(255);    // Máximo brilho
  oled.clear();
  oled.setFont(FONT8X16);
  oled.setCursor(0, 0);
  oled.print(("DIGISPARK OK"));
  oled.setFont(FONT6X8);
  oled.setCursor(0, 2);
  oled.print(F("SSD1306 I2C"));
}

void loop() {
}
