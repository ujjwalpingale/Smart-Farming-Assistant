# Smart Farming Assistant 🌱

Welcome to the **Smart Farming Assistant**, an AI-powered web application built to help farmers, agronomists, and agricultural enthusiasts make data-driven decisions. By combining modern machine learning models with a sleek, responsive web interface, this tool takes the guesswork out of farming and helps maximize crop yields.

---

## 🌟 What Does It Do?

This project features three main machine learning modules:

1. **🌾 Crop Recommendation**  
   Not sure what to plant? Input your soil's N-P-K (Nitrogen, Phosphorus, Potassium) levels, temperature, humidity, pH, and local rainfall. Our trained machine learning model will analyze the environmental data and recommend the optimal crop for your specific field conditions.

2. **🧪 Fertilizer Recommendation**  
   Provide your soil type, the crop you are growing, and the current nutrient levels in your soil. The system will give you a tailored fertilizer suggestion to fix any nutrient deficiencies and improve soil health without over-fertilizing.

3. **🔬 Plant Disease Detection**  
   Notice strange spots or wilting on your plant's leaves? Snap a photo and upload it! Our deep-learning Image Classification model will instantly analyze the image, identify the exact disease, and provide actionable prevention advice to save your harvest.

## 🛠️ Tech Stack

- **Frontend**: React.js & Vite (Featuring a custom, premium glassmorphism UI)
- **Backend**: Python & Django (Serving a robust JSON API)
- **Machine Learning**: Scikit-Learn (for Crop & Fertilizer models) and TensorFlow/Keras (for Image Disease Detection)

---

## 🚀 How to Run the Project Locally

Follow these steps to clone the repository and get the project running on your own machine. 

### Prerequisites
Make sure you have [Python 3.8+](https://www.python.org/downloads/) and [Node.js](https://nodejs.org/) installed on your computer.

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/smart_farming.git
cd smart_farming
```

### Step 2: Set Up the Backend (Django)

1. **Create and activate a virtual environment**:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install the required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory (you can copy `.env.example` if it exists) and add a Django Secret Key:
   ```env
   SECRET_KEY=your-super-secret-key-here
   DEBUG=True
   ```

4. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start the Django backend server**:
   ```bash
   python manage.py runserver
   ```
   *(Keep this terminal window open and running!)*

### Step 3: Set Up the Frontend (React/Vite)

1. Open a **new, second terminal window** and navigate into the `frontend` folder:
   ```bash
   cd frontend
   ```

2. **Install the Node dependencies**:
   ```bash
   npm install
   ```

3. **Start the frontend development server**:
   ```bash
   npm run dev
   ```

### Step 4: Use the Application!
Open your web browser and go to the frontend URL:
👉 **http://localhost:5173/**

*(Note: Ensure both servers are running simultaneously. Do not access the app via the port 8000 backend link directly).*

Create a free account, log in, and start analyzing your agricultural data!

---

## 🧠 Important Notes on ML Models
- The crop and fertilizer features use pre-trained `.pkl` (pickle) files located in the `ml_models/` folder. 
- The disease detection feature requires a trained `.h5` deep learning model. The application expects to find a `plant_disease_model.h5` and a `labels.json` file inside the `ml_models/disease/` directory to function correctly. If TensorFlow is not installed, the disease module will safely display an error.

---
*Built with ❤️ for smarter, sustainable farming.*