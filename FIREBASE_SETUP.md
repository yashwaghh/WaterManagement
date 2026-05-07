# 🔧 Hardware Setup Guide — A-101 Live Sensor

This guide is for the person setting up the **ESP8266 + YF-S201** hardware node for flat **A-101**. Follow every step in order.

---

## 📦 What You Need

| # | Component | Notes |
|---|-----------|-------|
| 1 | **ESP8266** (NodeMCU / Wemos D1 Mini) | Any ESP8266 dev board works |
| 2 | **YF-S201** Water Flow Sensor | Hall-effect, 3 wires |
| 3 | **10kΩ Resistor** | Pull-up for sensor data pin |
| 4 | Jumper wires + Breadboard | — |
| 5 | USB cable | To flash code from your PC |
| 6 | **2.4 GHz WiFi** network | ⚠️ ESP8266 does NOT support 5 GHz |

---

## ⚡ Step 1 — Wire the Circuit

| Sensor Wire | ESP8266 Pin | Notes |
|:---|:---|:---|
| **RED (VCC)** | `VIN` / `5V` | Sensor needs 5V |
| **BLACK (GND)** | `GND` | Common ground |
| **YELLOW (DATA)** | `D2` (GPIO4) | Add 10kΩ pull-up between Data and 3.3V |

---

## 🔥 Step 2 — Set Up Firebase

You need your **own** Firebase project. The software developer's Firebase keys are separate.

1. Go to [Firebase Console](https://console.firebase.google.com/) → **Create Project**
2. Enable **Realtime Database** → Create in **test mode**
3. Copy the **Database URL** (e.g. `https://my-aqua-project-default-rtdb.firebaseio.com`)
4. Enable **Authentication** → **Email/Password** sign-in method
5. Go to **Project Settings** → **Service Accounts** → **Generate New Private Key**
   - Save the downloaded `.json` file as `service_account.json` in the project root

### Create the A-101 User Account

In Firebase Console → **Authentication** → **Add User**:

| Field | Value |
|-------|-------|
| **Email** | `a101@aquasync.local` |
| **Password** | `water101` |

> You'll use this to log into the AquaSync dashboard and see your flat's data.

---

## 📝 Step 3 — Configure Environment Files

### Backend (`/.env`)
```bash
cp .env.example .env
```
Then edit `.env`:
```env
FIREBASE_SERVICE_ACCOUNT_PATH=./service_account.json
FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com
DATA_MODE=hybrid
```

### Frontend (`/frontend/.env`)
```bash
cp frontend/.env.example frontend/.env
```
Then fill in your Firebase Web App config. Get these from **Firebase Console → Project Settings → Your Apps → Add Web App**:
```env
REACT_APP_FIREBASE_API_KEY="your-api-key"
REACT_APP_FIREBASE_AUTH_DOMAIN="your-project.firebaseapp.com"
REACT_APP_FIREBASE_PROJECT_ID="your-project-id"
REACT_APP_FIREBASE_STORAGE_BUCKET="your-project.firebasestorage.app"
REACT_APP_FIREBASE_MESSAGING_SENDER_ID="your-sender-id"
REACT_APP_FIREBASE_APP_ID="your-app-id"
REACT_APP_FIREBASE_MEASUREMENT_ID="your-measurement-id"
```

### Hardware (`/hardware/credentials.h`)
```bash
cp hardware/credentials.h.example hardware/credentials.h
```
Then edit `credentials.h`:
```cpp
const char* ssid = "YourWiFiName";         // 2.4 GHz only!
const char* password = "YourWiFiPassword";
const char* firebaseHost = "https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com";
```

---

## 💻 Step 4 — Flash the ESP8266

1. Install [Arduino IDE](https://www.arduino.cc/en/software)
2. **Add ESP8266 Board**: `File` → `Preferences` → Additional Board URLs:
   ```
   http://arduino.esp8266.com/stable/package_esp8266com_index.json
   ```
3. `Tools` → `Board` → `Boards Manager` → Search `esp8266` → Install
4. **Select board**: `Tools` → `Board` → `NodeMCU 1.0 (ESP-12E Module)`
5. Open `hardware/esp8266_water_sensor.cpp` in Arduino IDE
   - You may need to rename it to `.ino` or place inside a folder with the same name
6. Connect ESP8266 via USB, select the correct **COM Port**
7. Hit **Upload** ▶️

---

## 🖥️ Step 5 — Run the Application

```bash
# Terminal 1 — Backend (from project root)
pip install -r requirements-api.txt
python api.py

# Terminal 2 — Frontend (from /frontend)
cd frontend
npm install
npm start
```

Or use the one-click launcher:
```bash
# Windows
start.bat

# PowerShell
./start.ps1
```

---

## 🔐 Step 6 — Log into the Dashboard

1. Open `http://localhost:3000`
2. Click **Sign Up** and register with:
   - **Email**: `a101@aquasync.local`
   - **Password**: `water101`
3. Complete the onboarding:
   - **Flat ID**: Select `A-101`
   - **Family Size**: Enter your household size (this sets your daily water limit)
4. Your dashboard will show **REAL** data from the sensor alongside 4 simulated flats

---

## ✅ How to Verify It's Working

| What to Check | Expected |
|---|---|
| Arduino Serial Monitor (9600 baud) | `Flow (ml/min): XX.XX` printed every second |
| Firebase Console → Realtime Database | `/readings/A-101/current` updates live |
| AquaSync Dashboard → Leaderboard | A-101 shows `REAL` badge, others show `SIM` |
| Arduino HTTP Response | `HTTP Response: 200` in Serial Monitor |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| Flow always 0 | Check water direction matches arrow on sensor. Verify pull-up resistor. |
| WiFi won't connect | Must be **2.4 GHz**. ESP8266 cannot see 5 GHz networks. |
| Firebase PUT fails (HTTP -1) | Check `firebaseHost` URL. Remove trailing `/`. Ensure RTDB rules allow writes. |
| Dashboard shows no A-101 | Check `DATA_MODE=hybrid` in `.env`. Restart backend after changing. |
| "Firebase init failed" in backend logs | Verify `service_account.json` exists and path is correct in `.env` |

---

## 📊 What the Sensor Writes to Firebase

The ESP8266 PUTs this JSON to `/readings/A-101/current` every second:

```json
{
  "unique_id": "A-101",
  "water_used_ml": 840.5,
  "flow_rate_ml_min": 14.2,
  "daily_threshold_ml": 2500,
  "timestamp": "2026-05-07T15:30:00Z"
}
```

The backend reads this path and feeds it into the leaderboard, analytics, and reports.
