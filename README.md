# 🌾 AgroSmart AI — Full-Stack Farming Assistant

> An end-to-end AI-powered farming support system that helps farmers decide the best crops to grow and guides them through the entire crop lifecycle with smart notifications.

---

## 📸 Feature Overview

| Feature | Description |
|---|---|
| 🧠 ML Crop Prediction | Random Forest model trained on soil + weather data recommends top 3 crops |
| 🔄 Crop Rotation Logic | Avoids same crop, prioritizes rotation-friendly alternatives |
| 🌦️ Live Weather | OpenWeatherMap integration fetches real-time temp, humidity, rainfall |
| 📅 Lifecycle Timeline | Full day-wise task schedule (sowing → harvest) auto-generated |
| 🔔 Smart Notifications | Daily email alerts, rain-based irrigation skipping via APScheduler |
| 🤖 AI Chat | Claude-powered farming Q&A with Hindi/Marathi support |
| 📧 Email Alerts | Styled HTML emails via Gmail SMTP |

---

## 🏗️ Project Structure

```
agro-ai/
├── backend/                  # FastAPI application
│   ├── main.py               # App entry point
│   ├── database.py           # MongoDB Atlas connection
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment variable template
│   ├── models/
│   │   └── schemas.py        # Pydantic models for all collections
│   ├── middleware/
│   │   └── auth.py           # JWT auth + password hashing
│   ├── routers/
│   │   ├── auth.py           # POST /register, POST /login
│   │   ├── farm.py           # POST /farm/input, GET /farm/latest
│   │   ├── prediction.py     # POST /predict, POST /select-crop
│   │   ├── timeline.py       # GET /timeline/active, PATCH complete task
│   │   ├── notifications.py  # GET /history, POST /trigger-daily
│   │   └── chat.py           # POST /chat/message (AI assistant)
│   ├── services/
│   │   ├── weather.py        # OpenWeatherMap API client
│   │   ├── ml_predictor.py   # Load model + run predictions
│   │   ├── email_service.py  # Gmail SMTP async sender
│   │   └── timeline_generator.py  # Crop lifecycle schedule builder
│   └── scheduler/
│       ├── job_runner.py     # APScheduler — daily 7AM job
│       └── notification_logic.py  # Smart alert decision engine
│
├── ml/                       # Machine Learning
│   ├── train.py              # Train Random Forest model
│   ├── test_model.py         # Verify predictions
│   ├── data/                 # Place Crop_recommendation.csv here
│   └── artifacts/            # Saved model files (auto-generated)
│
├── frontend/                 # React + Vite + Tailwind
│   ├── src/
│   │   ├── App.jsx           # Router + AuthProvider
│   │   ├── main.jsx          # React entry point
│   │   ├── index.css         # Global Tailwind styles
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── services/
│   │   │   └── api.js        # Axios + all API helpers
│   │   ├── components/
│   │   │   └── Layout.jsx    # Sidebar nav + mobile menu
│   │   └── pages/
│   │       ├── LoginPage.jsx
│   │       ├── RegisterPage.jsx
│   │       ├── DashboardPage.jsx
│   │       ├── RecommendPage.jsx   # Farm input + crop selection
│   │       ├── TimelinePage.jsx    # Day-wise task tracker
│   │       ├── NotificationsPage.jsx
│   │       └── ChatPage.jsx        # AI chat interface
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── vercel.json
│
├── render.yaml               # Render.com backend deployment
└── .gitignore
```

---

## ⚡ Local Setup (Step by Step)

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [MongoDB Atlas](https://www.mongodb.com/atlas) account
- A free [OpenWeatherMap](https://openweathermap.org/api) API key
- Gmail account with [App Password](https://myaccount.google.com/apppasswords) enabled
- (Optional) [Anthropic API key](https://console.anthropic.com/) for AI chat

---

### Step 1 — Clone and set up

```bash
git clone https://github.com/yourusername/agro-ai.git
cd agro-ai
```

---

### Step 2 — Train the ML Model

```bash
# Install ML dependencies
pip install scikit-learn numpy pandas joblib

# Train the model (uses synthetic data if CSV not found)
python ml/train.py

# Expected output:
# ✅ Model Accuracy: ~95%
# 💾 Model artifacts saved to ml/artifacts/

# (Optional) Test predictions
python ml/test_model.py
```

> **Using the real dataset**: Download [Crop_recommendation.csv](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) from Kaggle and save it to `ml/data/Crop_recommendation.csv` before running `train.py`.

---

### Step 3 — Configure Backend

```bash
cd backend
cp .env.example .env
```

Edit `.env`:

```env
# MongoDB Atlas connection string
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/agrosmart?retryWrites=true&w=majority

# JWT — use any strong random string (min 32 chars)
JWT_SECRET=my-super-secret-key-change-this-immediately

# OpenWeatherMap (free tier)
OPENWEATHER_API_KEY=abc123yourkeyhere

# Gmail SMTP — use an App Password, NOT your main Gmail password
SMTP_USER=youremail@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx

# Anthropic (optional — chat works with mock responses without it)
ANTHROPIC_API_KEY=sk-ant-...

# Frontend URL for CORS
FRONTEND_URL=http://localhost:5173
```

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend
uvicorn main:app --reload --port 8000

# Swagger API docs available at:
# http://localhost:8000/docs
```

---

### Step 4 — Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create env file
echo "VITE_API_URL=http://localhost:8000/api" > .env.local

# Start development server
npm run dev

# App opens at: http://localhost:5173
```

---

## 🔌 API Reference

All endpoints are documented interactively at `http://localhost:8000/docs` (Swagger UI).

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT |

### Farm & Prediction
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/farm/input` | Save soil data |
| GET | `/api/farm/latest` | Get most recent farm input |
| POST | `/api/prediction/predict` | Run ML prediction + fetch weather |
| POST | `/api/prediction/select-crop` | Select a crop, generate timeline |

### Timeline
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/timeline/active` | Get active crop timeline |
| GET | `/api/timeline/all` | Get all past timelines |
| PATCH | `/api/timeline/{id}/task/{day}/complete` | Mark task done |

### Notifications & Chat
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/notifications/history` | All past notifications |
| POST | `/api/notifications/trigger-daily` | Manually trigger daily check |
| POST | `/api/chat/message` | Send AI chat message |

---

## 🗄️ MongoDB Collections

### `users`
```json
{
  "_id": "ObjectId",
  "name": "Rajesh Patil",
  "email": "rajesh@example.com",
  "password": "<bcrypt hash>",
  "location": "Pune",
  "created_at": "ISODate"
}
```

### `farm_data`
```json
{
  "user_id": "string",
  "soil": { "nitrogen": 80, "phosphorus": 40, "potassium": 40, "ph": 6.5, "moisture": 60 },
  "location": "Pune",
  "previous_crop": "wheat",
  "created_at": "ISODate"
}
```

### `predictions`
```json
{
  "user_id": "string",
  "farm_id": "string",
  "recommendations": [{ "crop": "rice", "confidence": 82.4, "is_rotation_friendly": true, "reason": "..." }],
  "selected_crop": "rice",
  "timeline_id": "string",
  "weather": { "temperature": 28, "humidity": 75, "rainfall": 120 },
  "created_at": "ISODate"
}
```

### `timelines`
```json
{
  "user_id": "string",
  "crop": "rice",
  "sowing_date": "2025-06-01",
  "active": true,
  "total_days": 110,
  "tasks": [
    {
      "day": 1,
      "task_type": "sowing",
      "title": "Seed Sowing",
      "description": "Sow pre-germinated seeds...",
      "scheduled_date": "2025-06-01",
      "completed": false,
      "skipped": false
    }
  ]
}
```

### `notifications`
```json
{
  "user_id": "string",
  "crop": "rice",
  "task_type": "irrigation",
  "message": "Rain expected (75%), irrigation skipped for today.",
  "date": "2025-06-05",
  "status": "skipped"
}
```

---

## 🚀 Deployment

### Backend → Render.com (Free)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — click **Deploy**
5. In **Environment** tab, add all your `.env` variables
6. Copy the service URL: `https://agrosmart-backend.onrender.com`

### Frontend → Vercel (Free)

1. Go to [vercel.com](https://vercel.com) → **Import Project** from GitHub
2. Set **Root Directory** to `frontend`
3. Add environment variable:
   - `VITE_API_URL` = `https://agrosmart-backend.onrender.com/api`
4. Click **Deploy**
5. Update `FRONTEND_URL` in Render to your Vercel domain

### Database → MongoDB Atlas (Free)

1. Create account at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a free **M0 cluster** (512MB, always free)
3. Create a database user with a strong password
4. Whitelist IP `0.0.0.0/0` (for Render.com dynamic IPs)
5. Get connection string from **Connect → Drivers**

---

## 📧 Gmail SMTP Setup

Gmail requires an **App Password** (not your regular password):

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. **Security** → Enable **2-Step Verification**
3. **Security** → **App passwords**
4. Select: App = "Mail", Device = "Other" → type "AgroSmart"
5. Copy the 16-character password → paste as `SMTP_PASSWORD`

---

## 🔔 Notification Logic (Smart Alerts)

The daily scheduler (APScheduler, 7:00 AM) runs this decision tree:

```
For each user with active timeline:
  For each task scheduled today:
    IF task_type == "irrigation":
      IF rain_probability > 70%:
        → Skip irrigation
        → Email: "Rain expected, irrigation skipped"
      ELSE:
        → Email: "Irrigation reminder for Day X"
    ELIF task_type == "fertilizer":
      → Email: "Apply fertilizer today (Day X)"
    ELIF task_type == "pest_check":
      → Email: "Scout your field today (Day X)"
    ELIF task_type == "harvest":
      → Email: "🎉 Harvest time! Day X"

  IF rain_probability > 80%:
    → Email: "Heavy rain alert — protect your crop"
```

To **test notifications manually** without waiting for 7AM:
```bash
# Via API (requires auth token)
POST /api/notifications/trigger-daily

# Or directly in Python
cd backend
python -c "
import asyncio
from database import connect_db
from scheduler.notification_logic import check_and_notify_user

async def main():
    await connect_db()
    # pass your user dict
    ...
asyncio.run(main())
"
```

---

## 🧪 Crop Rotation Map

The system knows which crops work well after which:

| Previous Crop | Recommended Next Crops |
|---|---|
| Rice | Wheat, Mustard, Chickpea, Lentil |
| Wheat | Rice, Maize, Cotton, Sugarcane |
| Cotton | Wheat, Chickpea, Lentil, Mustard |
| Maize | Wheat, Soybean, Groundnut, Sunflower |
| Chickpea | Rice, Maize, Cotton, Wheat |

Rotation-friendly crops are ranked first in the recommendation list, marked with a ✅ badge.

---

## 🌐 Multilingual Support

The AI chat supports:
- 🇬🇧 **English** (default)
- 🇮🇳 **Hindi** (हिंदी)
- 🌸 **Marathi** (मराठी)

Select language from the dropdown in the chat page. The Claude AI model responds in the selected language automatically.

---

## 🔥 Bonus / Future Features

| Feature | Status | Notes |
|---|---|---|
| SMS Notifications | Future | Integrate Twilio or Fast2SMS |
| Market Price Prediction | Future | Scrape Agmarknet data |
| Voice Input | Future | Web Speech API |
| Offline PWA | Future | Service Worker + IndexedDB |
| Satellite Field Monitoring | Future | Sentinel Hub API |

---

## 🛠️ Tech Stack Summary

| Layer | Technology | Why |
|---|---|---|
| Frontend | React 18 + Vite + Tailwind CSS | Fast, modern, mobile-friendly |
| Backend | Python FastAPI | Async, auto-swagger, production-ready |
| Database | MongoDB Atlas (Motor async) | Flexible schema, free tier |
| ML | Scikit-learn Random Forest | High accuracy, fast inference |
| Weather | OpenWeatherMap API | Free tier, 60 calls/min |
| Email | Gmail SMTP (aiosmtplib) | Free, reliable |
| AI Chat | Anthropic Claude | Best-in-class reasoning |
| Scheduler | APScheduler | In-process, no Redis needed |
| Auth | JWT + bcrypt | Industry standard |
| Hosting | Vercel + Render | Both have generous free tiers |

---

## 📝 License

MIT License — free to use, modify, and deploy.

---

*Built with ❤️ for Indian farmers — improving yields through AI-powered decisions.*
