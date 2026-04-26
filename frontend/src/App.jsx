import { Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Exams from './pages/Exams';
import ExamDetail from './pages/ExamDetail';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import Quiz from './pages/Quiz';
import Resources from './pages/Resources';
import News from './pages/News';
import PracticeQuiz from './pages/PracticeQuiz';
import Groups from './pages/Groups';
import GroupDetail from './pages/GroupDetail';

function App() {
  return (
    <div className="min-h-screen bg-light-bg font-sans text-gray-900 selection:bg-india-saffron selection:text-white">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/exams" element={<ProtectedRoute><Exams /></ProtectedRoute>} />
          <Route path="/exams/:id" element={<ProtectedRoute><ExamDetail /></ProtectedRoute>} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/quiz" element={<ProtectedRoute><Quiz /></ProtectedRoute>} />
          <Route path="/practice-quiz" element={<ProtectedRoute><PracticeQuiz /></ProtectedRoute>} />
          <Route path="/resources" element={<ProtectedRoute><Resources /></ProtectedRoute>} />
          <Route path="/news" element={<ProtectedRoute><News /></ProtectedRoute>} />
          <Route path="/groups" element={<ProtectedRoute><Groups /></ProtectedRoute>} />
          <Route path="/groups/:id" element={<ProtectedRoute><GroupDetail /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
