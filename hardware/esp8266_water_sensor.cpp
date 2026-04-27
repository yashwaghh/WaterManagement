#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
#include <ESP8266HTTPClient.h>
#include <time.h>
#include "credentials.h"  // Copy credentials.h.example → credentials.h and fill in your values

// 🔹 Flow sensor
volatile int pulseCount = 0;

// 🔹 Water tracking
float totalUsage_ml = 0;

// 🔹 Interrupt
void IRAM_ATTR countPulse() {
  pulseCount++;
}

// 🔹 Timestamp (ISO format)
String getISOTime() {
  time_t now;
  time(&now);
  struct tm *timeinfo = gmtime(&now);

  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", timeinfo);
  return String(buffer);
}

void setup() {
  Serial.begin(9600);

  pinMode(D2, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(D2), countPulse, RISING);

  // WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected");

  // NTP
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  while (time(nullptr) < 100000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nTime synced");
}

void loop() {

  delay(1000); // 1 second sampling

  noInterrupts();
  int pulses = pulseCount;
  pulseCount = 0;
  interrupts();

  // ✅ Correct YF-S201 calculation
  float flow_L_min = pulses / 7.5;
  float flow_ml_min = flow_L_min * 1000.0;

  // Convert to ml/sec
  float flow_ml_sec = flow_ml_min / 60.0;

  // Accumulate usage
  totalUsage_ml += flow_ml_sec;

  Serial.println("Flow (ml/min): " + String(flow_ml_min));
  Serial.println("Total Used (ml): " + String(totalUsage_ml));

  // 🔥 Send to Firebase
  if (WiFi.status() == WL_CONNECTED) {

    WiFiClientSecure client;
    client.setInsecure();
    HTTPClient http;

    // ✅ CORRECT PATH (IMPORTANT)
    String url = String(firebaseHost) + "/readings/A-101/current.json";

    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"unique_id\":\"A-101\",";
    json += "\"water_used_ml\":" + String(totalUsage_ml, 2) + ",";
    json += "\"flow_rate_ml_min\":" + String(flow_ml_min, 2) + ",";
    json += "\"daily_threshold_ml\":2500,";
    json += "\"timestamp\":\"" + getISOTime() + "\"";
    json += "}";

    int code = http.PUT(json);

    Serial.print("HTTP Response: ");
    Serial.println(code);

    http.end();
  }
}