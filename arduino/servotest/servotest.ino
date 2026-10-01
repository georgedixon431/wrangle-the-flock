#include <ESP32Servo.h>

Servo myServo;

const int SERVO_PIN = 4;

void setup() {
  Serial.begin(115200);

  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, 500, 2500);

  Serial.println("Servo test starting");
}

void loop() {
  Serial.println("0 degrees");
  myServo.write(0);
  delay(3000);

  Serial.println("90 degrees");
  myServo.write(90);
  delay(3000);

  Serial.println("180 degrees");
  myServo.write(180);
  delay(3000);

  Serial.println("90 degrees");
  myServo.write(90);
  delay(3000);
}