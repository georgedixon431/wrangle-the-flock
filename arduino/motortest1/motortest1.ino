// Motor 1
const int M1_RPWM = 12;
const int M1_LPWM = 13;

// Motor 2
const int M2_RPWM = 32;
const int M2_LPWM = 33;

void setup() {
  Serial.begin(115200);

  pinMode(M1_RPWM, OUTPUT);
  pinMode(M1_LPWM, OUTPUT);
  pinMode(M2_RPWM, OUTPUT);
  pinMode(M2_LPWM, OUTPUT);

  // Both motors stopped initially
  digitalWrite(M1_RPWM, LOW);
  digitalWrite(M1_LPWM, LOW);
  digitalWrite(M2_RPWM, LOW);
  digitalWrite(M2_LPWM, LOW);

  Serial.println("ESP32 started");
}

void loop() {
  // Motor 1 runs for 5 seconds
  Serial.println("MOTOR 1 RUNNING");
  digitalWrite(M1_RPWM, HIGH);
  digitalWrite(M1_LPWM, LOW);

  digitalWrite(M2_RPWM, LOW);
  digitalWrite(M2_LPWM, LOW);

  delay(5000);

  // Both motors stop for 2 seconds
  Serial.println("BOTH MOTORS STOPPED");
  digitalWrite(M1_RPWM, LOW);
  digitalWrite(M1_LPWM, LOW);
  digitalWrite(M2_RPWM, LOW);
  digitalWrite(M2_LPWM, LOW);

  delay(2000);

  // Motor 2 runs for 5 seconds
  Serial.println("MOTOR 2 RUNNING");
  digitalWrite(M1_RPWM, LOW);
  digitalWrite(M1_LPWM, LOW);

  digitalWrite(M2_RPWM, HIGH);
  digitalWrite(M2_LPWM, LOW);

  delay(5000);

  // Both motors stop for 2 seconds
  Serial.println("BOTH MOTORS STOPPED");
  digitalWrite(M1_RPWM, LOW);
  digitalWrite(M1_LPWM, LOW);
  digitalWrite(M2_RPWM, LOW);
  digitalWrite(M2_LPWM, LOW);

  delay(2000);
}