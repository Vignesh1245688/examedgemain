# Exam Awareness Platform 🚀

A comprehensive digital platform designed to provide awareness and resources for various competitive exams. This project features a robust Django backend and a modern React frontend built with Vite.

## 🌟 Features

- **Live News Updates**: Real-time news fetching using external APIs to keep candidates updated on the latest exam notifications.
- **YouTube Resource Integration**: Curated educational resources and study materials from YouTube.
- **Exam Information**: Detailed insights and awareness about various competitive examinations.
- **User Authentication**: Secure login and registration for personalized experiences.

## 🛠️ Tech Stack

- **Frontend**: React.js, Vite, Tailwind CSS
- **Backend**: Django (Python)
- **Database**: SQLite (Default)
- **APIs**: NewsAPI, YouTube Data API, Google Custom Search

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites
- Node.js (LTS)
- Python 3.10+

### Step 1: Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Activate the virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the server:
   ```bash
   python manage.py runserver
   ```

### Step 2: Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 🔑 Environment Variables

The project requires several API keys to function correctly. Create a `.env` file in the `backend/` directory with the following variables:

```env
NEWS_API_KEY=your_news_api_key
YOUTUBE_API_KEY=your_youtube_api_key
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
GOOGLE_CX=your_search_engine_id
```

> [!IMPORTANT]
> Never commit your `.env` file to the repository. It is included in the `.gitignore`.

---
*Created by [akash14-coder](https://github.com/akash14-coder)*
