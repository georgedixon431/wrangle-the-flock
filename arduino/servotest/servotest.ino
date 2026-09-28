#include <ESP32Servo.h>

Servo myServo;

// Servo PWM pin from your diagram
const int SERVO_PIN = 4;

void setup() {
  // MG996R uses standard servo pulse range
  myServo.setPeriodHertz(50);

  // Attach servo to ESP32
  myServo.attach(SERVO_PIN, 500, 2500);

  // Start at 0 degrees
  myServo.write(0);

  delay(3000);
}

void loop() {

  // Move to 180 degrees
  myServo.write(180);

  delay(3000);

  // Move back to 0 degrees
  myServo.write(0);

  delay(3000);
}