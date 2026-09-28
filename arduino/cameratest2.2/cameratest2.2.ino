#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char* WIFI_SSID = "ORBI80";
const char* WIFI_PASS = "rockypotato037";

WebServer server(80);

const int PIN_FLASH = 4;

// Maximum OV2640 resolution
static auto oneRes = esp32cam::Resolution::find(1600, 1200);

void serveJpg()
{
  auto frame = esp32cam::capture();

  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "text/plain", "capture failed");
    return;
  }

  Serial.printf("CAPTURE: %dx%d | %d bytes\n",
                frame->getWidth(),
                frame->getHeight(),
                (int)frame->size());

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");

  WiFiClient client = server.client();
  frame->writeTo(client);
}

void setup()
{
  Serial.begin(115200);
  Serial.println();

  // Flash LED
  pinMode(PIN_FLASH, OUTPUT);
  digitalWrite(PIN_FLASH, LOW);

  {
    using namespace esp32cam;

    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(oneRes);
    cfg.setBufferCount(1);
    cfg.setJpeg(8);

    bool ok = Camera.begin(cfg);

    if (!ok) {
      Serial.println("CAMERA FAIL");
      return;
    }

    Serial.println("CAMERA OK");
    Serial.println("Resolution: 1600x1200");
    Serial.println("JPEG quality: 8");
  }

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected");

  server.on("/cam.jpg", serveJpg);
  server.begin();

  Serial.println("Camera server running");

  // Flash light for 1 second to show system is ready
  Serial.println("FLASH ON");
  digitalWrite(PIN_FLASH, HIGH);
  delay(1000);
  digitalWrite(PIN_FLASH, LOW);
  Serial.println("FLASH OFF");

  Serial.print("Camera: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/cam.jpg");
}

void loop()
{
  server.handleClient();
}