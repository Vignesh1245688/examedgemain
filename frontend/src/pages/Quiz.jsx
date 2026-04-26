import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axiosConfig';
import { Clock, CheckCircle, AlertCircle, RefreshCcw } from 'lucide-react';

const Quiz = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes

  const navigate = useNavigate();

  useEffect(() => {
    fetchQuestions();
  }, []);

  useEffect(() => {
    let timer;
    if (!loading && !result && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && !result) {
      handleSubmitQuiz();
    }
    return () => clearInterval(timer);
  }, [timeLeft, loading, result]);

  const fetchQuestions = async () => {
    try {
      const res = await api.get('quiz/');
      setQuestions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOptionSelect = (qId, optionVal) => {
    setAnswers({
      ...answers,
      [qId]: optionVal,
    });
  };

  const handleSubmitQuiz = async () => {
    try {
      // Format answers as required by DRF: { "1": "A", "2": "C" }
      const res = await api.post('quiz/submit/', { answers });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert('Error submitting quiz.');
    }
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  if (loading) return (
    <div className="pt-24 min-h-screen flex justify-center bg-light-bg">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-navy-blue mt-20"></div>
    </div>
  );

  if (questions.length === 0) return (
    <div className="pt-24 min-h-screen bg-light-bg text-center">
      <h2 className="text-2xl font-bold text-gray-700 mt-10">No questions available right now.</h2>
      <button onClick={() => navigate('/dashboard')} className="mt-4 text-navy-blue hover:underline">Return to Dashboard</button>
    </div>
  );

  // Result View
  if (result) {
    return (
      <div className="min-h-screen bg-light-bg pt-24 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
        <div className="bg-white max-w-lg w-full rounded-2xl p-8 shadow-lg border border-gray-100 text-center">
          <div className="w-20 h-20 bg-green-50 text-india-green rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10" />
          </div>
          <h2 className="text-3xl font-extrabold text-navy-blue mb-2">Quiz Completed!</h2>
          <p className="text-gray-600 mb-8">Here is your performance summary:</p>
          
          <div className="grid grid-cols-2 gap-4 mb-8 text-left">
            <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
               <p className="text-sm text-gray-500 mb-1">Score</p>
               <p className="text-2xl font-bold text-navy-blue">{result.score} / {result.total}</p>
            </div>
             <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
               <p className="text-sm text-gray-500 mb-1">Accuracy</p>
               <p className="text-2xl font-bold text-india-green">
                 {Math.round((result.score / result.total) * 100)}%
               </p>
            </div>
          </div>

          <button 
            onClick={() => window.location.reload()}
            className="w-full flex justify-center items-center py-3 px-4 rounded-full text-white bg-navy-blue hover:bg-opacity-90 transition-all shadow-sm font-medium"
          >
            <RefreshCcw className="w-5 h-5 mr-2" /> Take Another Quiz
          </button>
          <button 
            onClick={() => navigate('/dashboard')}
            className="w-full mt-4 flex justify-center py-3 px-4 border border-gray-200 rounded-full text-gray-700 bg-white hover:bg-gray-50 transition-all font-medium"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Active Quiz View
  const question = questions[currentQuestionIdx];
  const qId = question.id;
  const isLastQuestion = currentQuestionIdx === questions.length - 1;

  return (
    <div className="min-h-screen bg-light-bg pt-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        
        {/* Quiz Header */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-6 flex justify-between items-center sticky top-24 z-10">
          <div>
            <span className="text-sm font-semibold text-india-saffron uppercase tracking-wider">Practice Exam</span>
            <h2 className="text-xl font-bold text-navy-blue">General Studies Mock</h2>
          </div>
          <div className={`flex items-center px-4 py-2 rounded-full font-bold ${timeLeft < 60 ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-blue-50 text-navy-blue border border-blue-100'}`}>
            <Clock className="w-5 h-5 mr-2" />
            {formatTime(timeLeft)}
          </div>
        </div>

        {/* Status Bar */}
        <div className="flex justify-between items-center mb-6 text-sm font-medium text-gray-500">
          <span>Question {currentQuestionIdx + 1} of {questions.length}</span>
          <div className="flex gap-1">
            {questions.map((q, idx) => (
              <div 
                key={q.id} 
                className={`w-2 h-2 rounded-full ${idx === currentQuestionIdx ? 'bg-navy-blue scale-150' : answers[q.id] ? 'bg-india-green' : 'bg-gray-300'}`}
              />
            ))}
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 mb-8">
          <div className="mb-4">
            <span className="px-3 py-1 bg-gray-100 text-gray-600 text-xs font-semibold rounded-full uppercase tracking-wider">
              {question.subject}
            </span>
          </div>
          <h3 className="text-xl md:text-2xl font-semibold text-gray-900 mb-8 leading-relaxed">
            {question.question_text}
          </h3>

          <div className="space-y-4">
            {['A', 'B', 'C', 'D'].map((opt) => (
              <label 
                key={opt} 
                className={`flex items-center p-4 border rounded-xl cursor-pointer transition-all ${
                  answers[qId] === opt 
                    ? 'border-navy-blue bg-blue-50/50 shadow-sm' 
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className={`w-6 h-6 rounded-full border flex items-center justify-center mr-4 flex-shrink-0 ${
                   answers[qId] === opt ? 'border-navy-blue bg-navy-blue text-white' : 'border-gray-300 text-gray-500'
                }`}>
                  <span className="text-sm font-medium">{opt}</span>
                </div>
                <span className={`text-gray-800 ${answers[qId] === opt ? 'font-medium' : ''}`}>
                  {question[`option_${opt.toLowerCase()}`]}
                </span>
                <input 
                  type="radio" 
                  name={`question-${qId}`} 
                  value={opt}
                  checked={answers[qId] === opt}
                  onChange={() => handleOptionSelect(qId, opt)}
                  className="hidden"
                />
              </label>
            ))}
          </div>
        </div>

        {/* Navigation Controls */}
        <div className="flex justify-between items-center border-t border-gray-200 pt-6">
          <button
            onClick={() => setCurrentQuestionIdx(prev => prev - 1)}
            disabled={currentQuestionIdx === 0}
            className="px-6 py-3 rounded-full font-medium text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          
          {isLastQuestion ? (
            <button
              onClick={handleSubmitQuiz}
              className="px-8 py-3 rounded-full font-bold text-white bg-india-green hover:bg-opacity-90 transition-all shadow-md shadow-india-green/30"
            >
              Submit Quiz
            </button>
          ) : (
            <button
               onClick={() => setCurrentQuestionIdx(prev => prev + 1)}
               className="px-8 py-3 rounded-full font-bold text-white bg-navy-blue hover:bg-opacity-90 transition-all shadow-md shadow-navy-blue/30"
            >
              Next Question
            </button>
          )}
        </div>

      </div>
    </div>
  );
};

export default Quiz;
