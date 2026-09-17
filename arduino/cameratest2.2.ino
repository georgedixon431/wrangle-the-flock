#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char* WIFI_SSID = "ORBI80";
const char* WIFI_PASS = "rockypotato037";

WebServer server(80);
const int PIN_FLASH = 4; // ESP32-CAM flash LED

// Pick ONE resolution. SVGA(800x600) is a good balance; increase if stable.
// You can try UXGA/SXGA if your module + PSRAM can handle it.
static auto oneRes = esp32cam::Resolution::find(640, 480);  // SVGA

void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "text/plain", "capture failed");
    return;
  }

  Serial.printf("OK %dx%d %dB\n", frame->getWidth(), frame->getHeight(),
                (int)frame->size());

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleJpg()
{
  // No resolution changes per request — keeps things stable & fast.
  serveJpg();
}

void setup() {
  Serial.begin(115200);
  Serial.println();

  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(oneRes);  // set ONCE
    cfg.setBufferCount(3);      // more buffers = smoother capture
    // NOTE: On many ESP32-CAM libs, LOWER number = HIGHER quality.
    // Try 10–15 for high quality, 20–30 for balanced, 40+ for small files.
    cfg.setJpeg(12);            // high quality (adjust if frames drop)

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("http://"); Serial.println(WiFi.localIP());
  Serial.println("  /cam.jpg");

  // Single endpoint
  server.on("/cam.jpg", handleJpg);

  server.begin();

}

void loop() {
  server.handleClient();
}
