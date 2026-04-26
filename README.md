# 💧 SDG Water Management Dashboard

A modern, real-time water management analytics system designed to track, analyze, and optimize water usage across multiple residential units (flats).

This project features:
- A rich dashboard showing live water consumption metrics.
- Rank & efficiency scoring (Leaderboard).
- A unified architecture combining a **React Frontend** and a **Flask Backend**.
- Seamless integration with **Firebase** to gather real sensor data, as well as a robust local **Simulator**.

---

## 🚀 Quick Start / Local Setup

Follow these steps to clone and run the project strictly on your local machine.

### 1. Prerequisites
- Python 3.11+
- Node.js 18+

### 2. Install Dependencies
**Backend Setup:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-api.txt
```

**Frontend Setup:**
```bash
cd frontend
npm install
cd ..
```

### 3. Configure Environment Variables
You must set up your environment properties. Duplicate the `.env.example` file and rename it to `.env`:
```bash
cp .env.example .env
```
_(Make sure your `service_account.json` is accurately mapped in the `.env` if you choose to use real Firebase bindings)_

### 4. Run Locally
The easiest way to start both the React frontend and Flask API locally in development mode is to use the start script:
```bash
bash start.sh
```
- **React App**: http://localhost:3000
- **Flask API**: http://localhost:5000/api

*(Alternatively, you can just start `api.py` and `npm start` in separate terminal windows).*

---

## ☁️ Deployment (Google Cloud Run)

The repository has been structured into a unified **Multi-Stage Docker container** to be deployed seamlessly on **Google Cloud Run** with absolutely no clutter. The backend dynamically serves the packaged frontend application.

### Prerequisites
- [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install) installed and authenticated.
- A Google Cloud Project with the **Cloud Run** and **Cloud Build** APIs enabled.

### Deploy Steps

Run the following command from the root of the repository:

```bash
gcloud run deploy water-dashboard \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

**What happens?**
1. Cloud Build automatically detects the `Dockerfile` at the root.
2. Stage 1 compiles the optimized React static build.
3. Stage 2 packages the Flask application and copies the React assets.
4. Google Cloud Run provisions a scalable HTTPS endpoint natively running the entire solution on port `8080`.

---

## 📊 Alternative: Streamlit Dashboard

If you prefer an ad-hoc python-native data dashboard over the React frontend, this repo includes `app.py`. 

To launch:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🛠 Project Structure

- `api.py` : Core Flask Backend application (Serves API + React frontend block).
- `app.py` : Alternative standalone Streamlit application.
- `simulator.py` : Built-in water flow Simulator.
- `src/` : Analytics and Ranking models.
- `frontend/` : The React Application source code. 
- `Dockerfile` : Production-grade Docker multi-stage environment container.

## 📄 License
MIT License
