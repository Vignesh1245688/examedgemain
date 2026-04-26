# How to Run the Project

This project consists of a Python Django backend and a React (Vite) frontend.

## Prerequisites
- Node.js (for the frontend)
- Python (for the backend)

---

## 1. Running the Backend (Django)

The backend is located in the `backend` folder and uses a virtual environment.

Open a terminal and run the following commands:
```bash
# Navigate to the backend directory
cd backend

# On Windows, activate the virtual environment and start the server in one command:
.\venv\Scripts\python manage.py runserver
```

The server should start running at `http://127.0.0.1:8000/`.

*(Note: If the virtual environment does not contain the necessary packages, you might need to install them using `.\venv\Scripts\pip install -r requirements.txt` if a requirements file is added later, but based on the current setup, dependencies are already installed in the `venv`.)*

---

## 2. Running the Frontend (React + Vite)

The frontend is located in the `frontend` folder.

Open a separate terminal and run the following commands:
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies (only required the first time, or when dependencies change)
npm install

# Start the development server
npm run dev
```

The application will be accessible at `http://localhost:5173/`.
