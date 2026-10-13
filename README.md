# 🌱 Smart Farming Assistant

Hi there! This is our MCA final year project. We built this **Smart Farming Assistant** to help farmers use modern technology like AI and Machine Learning to make better decisions for their farms.

---

## 🤔 What does this project do?

Farming today is hard because of changing weather and soil issues. Our app helps solve this by providing four main tools:

1. **🌾 Crop Picker** — Enter your soil details (Nitrogen, Phosphorus, Potassium, etc.) and the AI recommends the top 3 crops best suited for your field.
   - **Smart Feature**: Automatically fetches live local weather when you select your District and Taluka in Maharashtra. No manual temperature input needed!

2. **🧪 Fertilizer Guide** — Detects nutrient deficiencies in your soil and recommends the exact fertilizer to fix it.

3. **🔬 Disease Doctor** — Upload a photo of your sick plant. The app uses Deep Learning to identify the disease and gives treatment advice.

4. **🤖 AI Farming Chatbot** — An AI assistant (powered by Google Gemini) that answers any farming question.
   - Supports **English**, **Marathi (मराठी)**, and **Hindi (हिंदी)** 🇮🇳
   - **Voice input** supported — talk instead of type!

---

## 🌍 Language Support (English + Marathi + Hindi)

The **entire application works in Marathi and Hindi** alongside English. Farmers who are more comfortable with their local language can use every single feature of the app. Switch between all three languages with just one click!

| Language | Code | Script |
|----------|------|--------|
| English  | `en` | Latin  |
| Marathi  | `mr` | मराठी  |
| Hindi    | `hi` | हिंदी  |

---

## 🛠️ Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Frontend   | React + Vite                            |
| Backend    | Django (Python)                         |
| Database   | MySQL                                   |
| AI / ML    | Google Gemini API, Scikit-learn, TensorFlow |
| Weather    | OpenWeatherMap API                      |

---

## 📁 Project Structure

```
Smart_Farming_Assistant/
├── smart_farming/          ← Main project folder
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                ← Your secret keys go here (see setup)
│   ├── .env.example        ← Template for .env
│   ├── smart_farming/      ← Django project settings
│   ├── user_app/           ← Django app (API, models, views)
│   ├── ml_models/          ← Trained ML model files
│   ├── frontend/           ← React + Vite frontend
│   └── venv/               ← Python virtual environment
└── db.sqlite3              ← SQLite database
```

---

## ⚙️ Prerequisites

Make sure you have these installed before running the project:

- **Python** 3.10 or higher
- **Node.js** 18 or higher & **npm**
- **Git**

---

## 🏃‍♂️ How to Run Locally

### Step 1 — Clone the Project

```bash
git clone https://github.com/your-username/smart-farming-assistant.git
cd smart-farming-assistant/smart_farming
```

---

### Step 2 — Set Up Environment Variables

1. Copy the example env file:
   ```bash
   copy .env.example .env
   ```
2. Open `.env` and fill in your actual keys:
   ```
   SECRET_KEY=your-django-secret-key
   WEATHER_API_KEY=your_openweather_api_key
   GEMINI_API_KEY=your_gemini_api_key
   DEBUG=True
   ```
   - Get a free Gemini API key at: https://aistudio.google.com/
   - Get a free OpenWeatherMap key at: https://openweathermap.org/api

---

### Step 3 — Backend (Django) — Terminal 1

```powershell
# From inside the smart_farming/ folder:

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install Python dependencies (only needed once)
pip install -r requirements.txt

# Apply database migrations (only needed once)
python manage.py migrate

# Start the Django development server
python manage.py runserver
```

✅ Backend runs at: **http://127.0.0.1:8000**

---

### Step 4 — Frontend (React) — Terminal 2

Open a **new terminal window** and run:

```powershell
# Go to the frontend folder
cd smart_farming/frontend

# Install npm packages (only needed once)
npm install

# Start the frontend dev server
npm run dev
```

✅ Frontend runs at: **http://localhost:5173**

---

### Step 5 — Open the App

Open **http://localhost:5173** in your browser (Chrome recommended). 🎉

> Make sure **both** the backend (port 8000) and frontend (port 5173) servers are running at the same time.

---

## 👨‍💻 Developed By

| Name             | Role                  |
|------------------|-----------------------|
| Ujjwal Pingale   | Full Stack Developer  |
| Divya Karotra    | ML & AI Integration   |
| Chetna Ranglani  | Frontend & UI         |

- **Class**: MCA Final Year
- **College**: Vivekanand Education Society's Institute of Technology (VESIT), Chembur, Mumbai
- **Academic Year**: 2026–27

---

*We hope this project helps in making farming a bit easier and smarter! 🌾*