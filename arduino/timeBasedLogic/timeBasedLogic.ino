#include <ESP32Servo.h>

// ==========================================
// M1 drives until either microswitch is hit.
// M1 then stops and M2 starts.
// ==========================================

// ---------- M1 / MD1 ----------
const int M1_RPWM = 25;
const int M1_LPWM = 33;

// ---------- M2 / MD2 ----------
const int M2_RPWM = 13;
const int M2_LPWM = 12;

// ---------- Microswitches ----------
const int LEFT_SWITCH  = 26;
const int RIGHT_SWITCH = 27;

Servo myServo;

const int SERVO_PIN = 32;
int ServoPosition = 0;

bool switchTriggered = false;

void setup() {
  Serial.begin(115200);
  Serial.println("SYSTEM STARTING");

  // M1
  pinMode(M1_RPWM, OUTPUT);
  pinMode(M1_LPWM, OUTPUT);

  // M2
  pinMode(M2_RPWM, OUTPUT);
  pinMode(M2_LPWM, OUTPUT);

  // Microswitches
  pinMode(LEFT_SWITCH, INPUT_PULLUP);
  pinMode(RIGHT_SWITCH, INPUT_PULLUP);

  // Make sure M2 starts OFF
  digitalWrite(M2_RPWM, LOW);
  digitalWrite(M2_LPWM, LOW);
  Serial.println("M2 STOPPED");

  // Start M1
  digitalWrite(M1_RPWM, LOW);
  digitalWrite(M1_LPWM, HIGH);
  Serial.println("M1 RUNNING");

  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, 500, 2500);
  ServoPosition = 0;
  Serial.println("gate open");

}

void loop() {
  int leftState = digitalRead(LEFT_SWITCH);
  int rightState = digitalRead(RIGHT_SWITCH);

  // Print switch states
  Serial.print("LEFT=");
  Serial.print(leftState == LOW ? "PRESSED" : "OPEN");
  Serial.print(" | RIGHT=");
  Serial.println(rightState == LOW ? "PRESSED" : "OPEN");

  // Check BOTH microswitches
  if (!switchTriggered && (leftState == LOW || rightState == LOW)) {
    switchTriggered = true;

    if (leftState == LOW) {
      Serial.println("LEFT MICROSWITCH TRIGGERED");
    }

    if (rightState == LOW) {
      Serial.println("RIGHT MICROSWITCH TRIGGERED");
    }

    // STOP M1
    digitalWrite(M1_RPWM, LOW);
    digitalWrite(M1_LPWM, LOW);
    Serial.println("M1 STOPPED");

    // Small pause before M2 starts
    Serial.println("WAITING 1 SECOND");
    delay(1000);

    // Run brush motor for 5 seconds
    digitalWrite(M2_RPWM, HIGH);
    digitalWrite(M2_LPWM, LOW);
    Serial.println("M2 RUNNING FOR 5 SECONDS");
    delay(5000);

    //stop brush motor
    digitalWrite(M2_RPWM, LOW);
    digitalWrite(M2_LPWM, LOW);

    //small pause before driving motor starts again
    delay(1000);
    digitalWrite(M1_RPWM, HIGH);
    digitalWrite(M1_LPWM, LOW);
    Serial.println("M1 Reversing");

    ServoPosition = 180;
    Serial.println("gate closed");
  } 

  myServo.write(ServoPosition);
  delay(200);
}