# Exam Awareness Platform - Project Execution Guide 🚀

This document provides a clean, step-by-step list of commands to get the **Digital Platform for Competitive Exam Awareness** up and running on your local machine.

---

## 📋 Prerequisites
Before starting, ensure you have the following installed:
*   **Python 3.10+**
*   **Node.js (LTS)** & **npm**
*   **VS Code** (Optional, but recommended)

---

## 🛠️ Step 1: Backend Setup (Django)
The backend handles the API logic, authentication, and live data fetching.

**1. Navigate to the backend directory:**
```powershell
cd backend
```

**2. Activate the Virtual Environment:**
```powershell
# Windows
.\venv\Scripts\activate
```

**3. Install Dependencies:**
*(Only if not already installed)*
```powershell
pip install -r requirements.txt
```

**4. Run Migrations:**
*(Ensures the database is ready)*
```powershell
python manage.py migrate
```

**5. Start the Backend Server:**
```powershell
python manage.py runserver
```

> [!NOTE]
> The backend will be available at: **http://127.0.0.1:8000**

---

## 💻 Step 2: Frontend Setup (React + Vite)
The frontend provides the user interface.

**1. Open a NEW terminal and navigate to the frontend directory:**
```powershell
cd frontend
```

**2. Install Dependencies:**
*(Only required the first time)*
```powershell
npm install
```

**3. Start the Development Server:**
```powershell
npm run dev
```

> [!NOTE]
> The frontend will be available at: **http://localhost:5173**

---

## 🔑 Step 3: API Key Configuration
For live News and Resources to work, ensure your `backend/.env` file contains valid keys:

```env
NEWS_API_KEY=fec9f537-f930-45a8-988e-e873ac9a5f3c
YOUTUBE_API_KEY=AIzaSyDn9N-XoRv...
GOOGLE_SEARCH_API_KEY=YOUR_KEY
GOOGLE_CX=YOUR_SEARCH_ENGINE_ID
```

---

## 💡 Quick Tips
*   **CORS Issues?** Ensure the backend is running. The frontend depends on it.
*   **Port Busy?** If `5173` is taken, Vite will use `5174`.
*   **Export to PDF:** 
    *   **In VS Code:** Open this file, install the "Markdown PDF" extension, and use the command `Markdown PDF: Export (pdf)`.
    *   **In Browser:** Open the project in a browser, and use `Ctrl+P` (Print) and "Save as PDF".

---

*Happy Coding!* 🌟
