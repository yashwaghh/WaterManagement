# 💧 AquaSync (SDG Water Management Dashboard)

A modern, real-time water management analytics system designed to track, analyze, and optimize water usage across multiple residential units (flats).

This project features:
- A rich dashboard showing live water consumption metrics.
- Gamified Rank & efficiency scoring (Leaderboarding built around SDG 6.4 metrics).
- A unified architecture combining a **React Frontend** and a **Flask Backend API**.
- Seamless integration with **Firebase** to gather real IoT sensor data.
- Built-in localized **Simulator** to run dummy tests without physical hardware.

---

## 🚀 Quick Start / Local Setup

Follow these steps to clone and run the project rapidly on your local machine.

### 1. Prerequisites
- Python 3.11+
- Node.js 18+

### 2. Environment Variables & Secrets setup

**CRITICAL: NEVER commit `.env`, `service_account.json`, or `hardware/credentials.h` to GitHub.**

1. Duplicate `.env.example` and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```
2. (Optional Frontend Envs) Duplicate `frontend/.env.example` to `frontend/.env`.
3. If using Firebase, place your Firebase Service Account JSON file in the root directory and name it `service_account.json`. (Ensure this file is strictly listed in `.gitignore`).

### 3. Install Dependencies & Start the Project

The easiest way to start both the React frontend and Flask API locally in development mode is to use the start script:

**Bash/MacOS/Linux:**
```bash
bash start.sh
```

**Windows:**
```powershell
.\start.bat
# OR
.\start.ps1
```

*(Alternatively, you can manually start the backend with `python api.py` from your virtual environment, and the frontend with `npm start` inside the `frontend/` folder in separate terminal windows).*

- **React App**: http://localhost:3000
- **Flask API**: http://localhost:5000/api

---

## 🔧 Hardware Setup

Are you setting up the actual ESP8266 IoT hardware sensors for a physical deployment?
👉 **Please refer to the [Hardware Setup Guide](hardware/README.md)** located in the `hardware/` directory.

---

## ☁️ Deployment (Google Cloud Run / Docker)

The repository has been structured into a unified **Multi-Stage Docker container** to be deployed seamlessly on Cloud platforms (like Google Cloud Run) with absolutely no clutter.

### Deploy Steps

Run the following command from the root of the repository to deploy directly via gcloud:

```bash
gcloud run deploy aqua-sync \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**What happens?**
1. Docker builds the optimized React static build.
2. It packages the Flask application and copies the compiled React assets to be served securely on a production WSGI runtime.

---

## 📊 Alternative: Streamlit Dashboard

If you prefer an ad-hoc python-native data dashboard for data exploration instead of the full React platform, this repo includes a lightweight app. 

To launch:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 🛠 Project Structure

```text
├── api.py                   # Core Flask Backend application (Serves API + React frontend block).
├── app.py                   # Alternative standalone Streamlit application.
├── simulator.py             # Built-in water flow Simulator for testing without hardware.
├── start.*                  # Launch scripts for various OS.
├── service_account.json     # 🔒 Firebase Admin SDK key (Ignored in git)
├── .env                     # 🔒 Environment variables (Ignored in git)
├── src/                     # Backend Utilities.
│   ├── analytics.py         # Advanced ML / Data analytics aggregations
│   ├── ranking.py           # SDG 6.4 GAMIFIED Scoring & ranking engines
├── hardware/                # IoT Sensor codebase (C++)
│   ├── README.md            # Hardware specific documentation
│   ├── esp8266_water...cpp  # Core loop for the Microcontroller
│   └── credentials.h        # 🔒 Hardware WiFi/Firebase keys (Ignored in git)
├── frontend/                # React Application source code.
│   ├── src/                 # UI Components, State, Firebase Web config
│   └── .env                 # 🔒 Frontend keys (Ignored in git)
└── Dockerfile               # Production-grade Docker multi-stage environment container.
```

## 📄 License
MIT License
