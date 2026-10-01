#include <WiFi.h>
#include <ESP32Servo.h>

// ==========================================
// SYSTEM SEQUENCE
//
// 1. M1 drives forward
// 2. Microswitch is triggered
// 3. M1 stops
// 4. M2 starts
// 5. Wait for "10SHEEP" from Python
// 6. M2 stops
// 7. M1 drives in opposite direction
// ==========================================


// WiFi 
const char* WIFI_SSID = "ORBI80";
const char* WIFI_PASS = "rockypotato037";

WiFiServer server(8080);


//M1 / MD1
const int M1_RPWM = 25;
const int M1_LPWM = 33;


//M2 / MD2
const int M2_RPWM = 13;
const int M2_LPWM = 12;

//Microswitches 
const int LEFT_SWITCH  = 26;
const int RIGHT_SWITCH = 27;

Servo myServo;

const int SERVO_PIN = 32;
int ServoPosition = 0;


//  System states
enum SystemState {
  M1_FORWARD,
  M2_RUNNING,
  M1_REVERSE
};

SystemState state = M1_FORWARD;


// MOTOR FUNCTIONS

void stopM1() {
  digitalWrite(M1_RPWM, LOW);
  digitalWrite(M1_LPWM, LOW);
}

void forwardM1() {
  digitalWrite(M1_RPWM, LOW);
  digitalWrite(M1_LPWM, HIGH);
}

void reverseM1() {
  digitalWrite(M1_RPWM, HIGH);
  digitalWrite(M1_LPWM, LOW);
}

void stopM2() {
  digitalWrite(M2_RPWM, LOW);
  digitalWrite(M2_LPWM, LOW);
}

void startM2() {
  digitalWrite(M2_RPWM, HIGH);
  digitalWrite(M2_LPWM, LOW);
}


// ==========================================
// SETUP
// ==========================================

void setup() {

  Serial.begin(115200);
  Serial.println();
  Serial.println("SYSTEM STARTING");


  // ---------- Motor pins ----------

  pinMode(M1_RPWM, OUTPUT);
  pinMode(M1_LPWM, OUTPUT);

  pinMode(M2_RPWM, OUTPUT);
  pinMode(M2_LPWM, OUTPUT);


  //Microswitches

  pinMode(LEFT_SWITCH, INPUT_PULLUP);
  pinMode(RIGHT_SWITCH, INPUT_PULLUP);


  // Make motors safe initially

  stopM1();
  stopM2();

  // servo setup

  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, 500, 2500);
  ServoPosition = 0;
  Serial.println("gate open");


  //Connect WiFi 

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");

  Serial.print("MOTOR ESP32 IP: ");
  Serial.println(WiFi.localIP());


  // ---------- Start TCP server ----------

  server.begin();

  Serial.println("TCP server running on port 8080");


  // ---------- Start M1 ----------

  forwardM1();

  state = M1_FORWARD;

  Serial.println("M1 RUNNING FORWARD");
}


// ==========================================
// LOOP
// ==========================================

void loop() {

  // =====================================================
  // CHECK FOR COMMAND FROM PYTHON
  // =====================================================

  WiFiClient client = server.available();

  if (client) {

    String command = client.readStringUntil('\n');
    command.trim();

    Serial.print("COMMAND RECEIVED: ");
    Serial.println(command);


    // Python has confirmed 10 sheep
    if (command == "10SHEEP" && state == M2_RUNNING) {

      Serial.println("10 SHEEP CONFIRMED");

      // Stop M2
      stopM2();

      Serial.println("M2 STOPPED");

      // Small pause
      delay(1000);

      //close gate
      ServoPosition = 180;

      // Run M1 in opposite direction
      reverseM1();

      state = M1_REVERSE;

      Serial.println("M1 RUNNING IN REVERSE");
    }

    client.println("OK");
    client.stop();
  }


  // =====================================================
  // M1 MOVING FORWARD
  // =====================================================

  if (state == M1_FORWARD) {

    int leftState = digitalRead(LEFT_SWITCH);
    int rightState = digitalRead(RIGHT_SWITCH);


    // Check both microswitches
    if (leftState == LOW || rightState == LOW) {

      if (leftState == LOW) {
        Serial.println("LEFT MICROSWITCH TRIGGERED");
      }

      if (rightState == LOW) {
        Serial.println("RIGHT MICROSWITCH TRIGGERED");
      }


      // Stop M1
      stopM1();

      Serial.println("M1 STOPPED");


      // Pause before M2
      Serial.println("WAITING 1 SECOND");

      delay(1000);


      // Start M2
      startM2();

      state = M2_RUNNING;

      Serial.println("M2 RUNNING");
      Serial.println("WAITING FOR 10 SHEEP...");
    }
  }

  myServo.write(ServoPosition);
  delay(20);
}