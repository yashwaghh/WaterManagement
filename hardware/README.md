# 🔧 Hardware — ESP8266 Water Flow Sensor

This folder contains the ESP8266 firmware for the AquaSync live sensor node.

## Quick Start

> **📖 Full setup guide**: See [`../FIREBASE_SETUP.md`](../FIREBASE_SETUP.md) for the complete step-by-step instructions.

### 1. Configure credentials
```bash
cp credentials.h.example credentials.h
# Edit credentials.h with your WiFi + Firebase URL
```

### 2. Flash via Arduino IDE
- Board: **NodeMCU 1.0 (ESP-12E Module)**
- Port: Your ESP8266's COM port
- Upload `esp8266_water_sensor.cpp`

### 3. Verify
Open Serial Monitor at **9600 baud** — you should see:
```
WiFi Connected
Time synced
Flow (ml/min): 0.00
Total Used (ml): 0.00
HTTP Response: 200
```

## Files

| File | Purpose |
|------|---------|
| `esp8266_water_sensor.cpp` | Main firmware — reads YF-S201 sensor, pushes to Firebase |
| `credentials.h.example` | Template for WiFi + Firebase credentials |
| `credentials.h` | Your actual credentials (gitignored, never commit!) |

## Circuit Wiring

| Sensor Wire | ESP8266 Pin |
|:---|:---|
| RED (VCC) | `VIN` / `5V` |
| BLACK (GND) | `GND` |
| YELLOW (DATA) | `D2` (GPIO4) + 10kΩ pull-up to 3.3V |

## Login Credentials for Dashboard

After flashing, log into the AquaSync dashboard at `http://localhost:3000`:

| Field | Value |
|-------|-------|
| Email | `a101@aquasync.local` |
| Password | `water101` |
| Flat ID | `A-101` |