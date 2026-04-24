# 🌱 Smart Farming Assistant

Hi there! This is our MCA final year project. We built this **Smart Farming Assistant** to help our farmers use modern technology like AI and Machine Learning to make better decisions for their farms.

---

## 🤔 What does this project do?

Basically, farming today is hard because of changing weather and soil issues. Our app helps solve this by providing four main tools:

1.  **🌾 Crop Picker**: You put in your soil details (like Nitrogen, Phosphorus, etc.), and the AI tells you which 3 crops will grow best in your field. 
    *   **The Cool Part**: It can automatically fetch your local weather if you select your District and Taluka in Maharashtra. No need to type in the temperature manually!
    
2.  **🧪 Fertilizer Guide**: If your soil is weak in some nutrients, this tool tells you exactly which fertilizer you should use to fix it.

3.  **🔬 Disease Doctor**: If your plant looks sick, just upload a photo. The app uses "Deep Learning" to identify the disease and gives you advice on how to save your crop.

4.  **🤖 AI Farming Friend (Chatbot)**: We added a chatbot that works like ChatGPT but for farmers. You can ask it anything about farming. 
    *   It speaks both **English and Marathi**.
    *   You can even talk to it using your voice if you don't want to type!

---

## 🌍 Language Support (Marathi + English)
One of the most important parts of our project is that **the entire application works in Marathi**. We wanted to make sure that farmers who are more comfortable with their local language can easily use every single feature of the app. You can switch between English and Marathi with just one click!

---

## 🛠️ What we used to build this:

*   **Frontend**: React (for a fast and beautiful website).
*   **Backend**: Django (to handle the data and users).
*   **Database**: **SQLite** (to store user accounts and farm data securely).
*   **Brain (AI)**: Google Gemini (for the chat) and Scikit-learn (for the predictions).
*   **Data**: OpenWeatherMap (to get live weather details).

---

## 🏃‍♂️ How to run it on your computer:

It’s very easy! Just follow these steps:

### Step 0: Download the Project
1.  Open your terminal or command prompt.
2.  Clone the project: `git clone https://github.com/your-username/smart-farming-assistant.git`
3.  Go into the project folder: `cd smart-farming-assistant`

### Step 1: Prepare the Backend (Python)
1.  Activate your virtual environment: `venv\Scripts\activate`
2.  Install the needed libraries: `pip install -r requirements.txt`
3.  Start the server: `python manage.py runserver`

### Step 2: Prepare the Frontend (React)
1.  Open a **second** terminal and go into the `frontend` folder: `cd frontend`
2.  Install the packages: `npm install` (only need to do this once).
3.  Start the website: `npm run dev`

### Step 3: Open the app
*   Look at the terminal, it will give you a link (usually `http://localhost:5173`). 
*   Open that link in Chrome, and you're good to go!

---

## 👨‍💻 Developed By (Team of 3)
1.  **Ujjwal Pingale**
2.  **Divya Karotra**
3.  **Chetna Ranglani**

*   **Class**: MCA Final Year
*   **College**: Vivekanand Education Society’s Institute of Technology (VESIT), Chembur, Mumbai
*   **Academic Year**: 2026-27

---
*We hope this project helps in making farming a bit easier and smarter!*