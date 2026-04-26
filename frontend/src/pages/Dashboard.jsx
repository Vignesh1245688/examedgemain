import { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { User, MapPin, Target, Bookmark, ExternalLink } from 'lucide-react';
import api from '../api/axiosConfig';

const Dashboard = () => {
  const { user } = useContext(AuthContext);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (user) {
      api.get('practice-quiz/history/')
        .then(res => setHistory(res.data))
        .catch(err => console.error(err));
    }
  }, [user]);

  if (!user) {
    return (
      <div className="min-h-screen pt-24 text-center">
        Loading profile...
      </div>
    );
  }

  const { profile } = user;
  const bookmarks = profile?.bookmarks_detail || [];

  return (
    <div className="min-h-screen bg-light-bg pt-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto py-8">
        
        <h1 className="text-3xl font-bold text-navy-blue mb-8">My Dashboard</h1>
        
        <div className="grid md:grid-cols-3 gap-8">
          
          {/* Profile Sidebar */}
          <div className="md:col-span-1 space-y-6">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 relative overflow-hidden">
              <div className="absolute top-0 w-full h-16 bg-navy-blue left-0 right-0 z-0"></div>
              
              <div className="relative z-10 flex flex-col items-center mt-6">
                <div className="w-24 h-24 bg-white rounded-full p-1 shadow-md mb-4 flex items-center justify-center">
                  <div className="w-full h-full bg-blue-50 text-navy-blue rounded-full flex items-center justify-center text-3xl font-bold uppercase">
                     {user.first_name?.[0] || user.username?.[0]}
                  </div>
                </div>
                <h2 className="text-xl font-bold text-gray-900">{user.first_name} {user.last_name}</h2>
                <p className="text-gray-500 mb-6">@{user.username}</p>
                
                <div className="w-full space-y-4">
                  <div className="flex items-center text-sm text-gray-700">
                    <MapPin className="w-4 h-4 text-gray-400 mr-3" />
                    <span className="font-medium">State:</span> <span className="ml-auto">{profile?.state || 'N/A'}</span>
                  </div>
                  <div className="flex items-center text-sm text-gray-700">
                    <Target className="w-4 h-4 text-gray-400 mr-3" />
                    <span className="font-medium">Target Exam:</span> <span className="ml-auto">{profile?.target_exam || 'N/A'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="md:col-span-2 space-y-8">
            
            {/* Bookmarked Exams */}
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
              <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                <Bookmark className="w-5 h-5 text-india-saffron mr-2" /> Bookmarked Exams
              </h3>
              
              {bookmarks.length === 0 ? (
                <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                  <p className="text-gray-500 mb-4">You haven't saved any exams yet.</p>
                  <Link to="/exams" className="text-navy-blue font-medium hover:underline">
                    Browse Exam Directory
                  </Link>
                </div>
              ) : (
                <div className="grid sm:grid-cols-2 gap-4">
                  {bookmarks.map((exam) => (
                     <div key={exam.id} className="border border-gray-100 rounded-xl p-5 hover:border-gray-300 transition-colors bg-light-bg/50">
                        <Link to={`/exams/${exam.id}`} className="block">
                          <h4 className="font-bold text-navy-blue mb-1 truncate">{exam.name}</h4>
                          <p className="text-xs text-gray-500 mb-3">{exam.category}</p>
                          <div className="flex justify-between items-center text-sm">
                            <span className="text-gray-600 font-medium text-xs">View Details</span>
                            <ExternalLink className="w-4 h-4 text-gray-400" />
                          </div>
                        </Link>
                     </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Practice Quizzes History */}
            <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Practice Quizzes</h3>
                  <p className="text-gray-600 text-sm">Test your knowledge with our AI-driven question bank based on your PDFs.</p>
                </div>
                <Link to="/practice-quiz" className="ml-4 px-6 py-2 bg-india-green text-white rounded-full font-medium hover:bg-opacity-90 shadow-sm transition-all whitespace-nowrap">
                  Start a Quiz
                </Link>
              </div>

              {history.length > 0 && (
                <div className="mt-4 grid sm:grid-cols-2 gap-4">
                  {history.map((item) => (
                    <div key={item.id} className="border border-gray-100 rounded-xl p-4 hover:border-gray-300 transition-colors bg-light-bg/50">
                      <h4 className="font-bold text-navy-blue mb-1 truncate">{item.title}</h4>
                      <p className="text-xs text-gray-500 mb-2">File: {item.file_name}</p>
                      <div className="flex justify-between items-center text-sm font-medium">
                        <span className="text-india-saffron">Score: {item.score}/{item.total_questions}</span>
                        <span className="text-gray-600">{new Date(item.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
