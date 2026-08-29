# 🚀 Smart Farming Assistant — Deployment Guide

This project is configured as a **unified single-service architecture** where Django serves both the REST API, ML models, and the built React Single-Page Application (SPA) static files.

---

## 🛠️ Option 1: Deploy on Render.com (Recommended Free Option)

1. **Push your code to GitHub / GitLab**.
2. Log into [Render.com](https://render.com) and click **New +** $\rightarrow$ **Web Service**.
3. Connect your repository.
4. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn smart_farming.wsgi:application --bind 0.0.0.0:$PORT`
5. Add Environment Variables:
   - `SECRET_KEY`: *(Generate a random 50-character string)*
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*` (or your `.onrender.com` domain)
   - `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT` *(or connect Render MySQL database)*
   - `WEATHER_API_KEY`: *(Your OpenWeather API Key)*
   - `GEMINI_API_KEY`: *(Your Gemini API Key)*
6. Click **Deploy Web Service**!

---

## 🚂 Option 2: Deploy on Railway.app

1. Log into [Railway.app](https://railway.app) and create a **New Project**.
2. Add a **MySQL Database** service to the project.
3. Add your GitHub repository as a **GitHub Repo Service**.
4. Set the environment variables in Railway referencing your MySQL service variables.
5. Railway will automatically detect `Procfile` and `build.sh` and deploy your app!

---

## 🐳 Option 3: Deploy with Docker / Docker Compose

If you have a Virtual Private Server (VPS) like AWS EC2, DigitalOcean, or Linode:

1. Clone your repo onto the server:
   ```bash
   git clone <your-repo-url>
   cd smart_farming
   ```
2. Copy and set up your `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Run with Docker Compose:
   ```bash
   docker-compose up --build -d
   ```
4. Access your live application at `http://<your-server-ip>:8000`!

---

## 📁 Deployment File Overview

- `build.sh`: Script executed during deployment (installs Python modules, builds React frontend, collects static assets, runs migrations).
- `Procfile`: Configures web process launcher for Heroku / Render / Railway.
- `Dockerfile`: Multi-stage Docker container specification.
- `docker-compose.yml`: Automated MySQL + Django container setup.
- `render.yaml`: Blueprint for 1-click deployment on Render.
- `smart_farming/settings.py`: Includes `WhiteNoise` static file compression & React template integration.
