import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axiosConfig';
import { UploadCloud, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const PracticeQuiz = () => {
  const navigate = useNavigate();
  // Steps: setup, loading, active, result
  const [step, setStep] = useState('setup');
  const [file, setFile] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [selectedOptions, setSelectedOptions] = useState({});
  const [quizScore, setQuizScore] = useState(0);
  const [error, setError] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [startTime, setStartTime] = useState(null);

  // New features
  const [difficulty, setDifficulty] = useState('Medium');
  const [numQuestions, setNumQuestions] = useState(5);
  const [timeLimit, setTimeLimit] = useState(5);

  useEffect(() => {
    let timer;
    if (step === 'active' && timeRemaining > 0) {
      timer = setInterval(() => {
        setTimeRemaining((prev) => prev - 1);
      }, 1000);
    } else if (step === 'active' && timeRemaining === 0) {
      finishQuiz();
    }
    return () => clearInterval(timer);
  }, [step, timeRemaining]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const startGeneration = async () => {
    if (!file) {
      setError('Please select a PDF file first.');
      return;
    }
    setStep('loading');
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('difficulty', difficulty);
    formData.append('num_questions', numQuestions);

    try {
      const response = await api.post('practice-quiz/generate/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      if (response.data?.questions && response.data.questions.length > 0) {
        setQuestions(response.data.questions);
        setTimeRemaining(timeLimit * 60);
        setStep('active');
        setStartTime(Date.now());
      } else {
        throw new Error('No questions generated');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate quiz. Please try again.');
      setStep('setup');
    }
  };

  const handleOptionSelect = (index) => {
    setSelectedOptions((prev) => ({
      ...prev,
      [currentQuestionIdx]: index
    }));
  };

  const handleNext = () => {
    if (currentQuestionIdx < questions.length - 1) {
      setCurrentQuestionIdx((prev) => prev + 1);
    } else {
      finishQuiz();
    }
  };

  const finishQuiz = async () => {
    // Calculate Score
    let score = 0;
    questions.forEach((q, idx) => {
      if (selectedOptions[idx] === q.correctAnswer) {
        score += 1;
      }
    });
    setQuizScore(score);
    
    const timeTaken = Math.floor((Date.now() - startTime) / 1000);

    // Save result to backend
    try {
      await api.post('practice-quiz/save-result/', {
        title: `Practice: ${file.name.substring(0, 30)}`,
        file_name: file.name,
        score,
        total_questions: questions.length,
        time_taken_seconds: timeTaken,
      });
    } catch (e) {
      console.error('Failed to save result', e);
    }
    
    setStep('result');
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  if (step === 'setup') {
    return (
      <div className="min-h-screen bg-light-bg pt-24 px-4">
        <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
          <h1 className="text-3xl font-bold text-navy-blue mb-4 text-center">Smart PDF Practice Quiz</h1>
          <p className="text-gray-600 mb-8 text-center text-sm md:text-base">Upload any study material (PDF) and our AI will instantly generate a tailored practice test to check your understanding.</p>
          
          {error && (
            <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-xl flex items-center text-sm">
              <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
              {error}
            </div>
          )}

          <div className="border-2 border-dashed border-gray-300 rounded-2xl p-10 flex flex-col items-center justify-center bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer relative">
            <input type="file" accept="application/pdf" onChange={handleFileChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
            <UploadCloud className="w-16 h-16 text-navy-blue mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-1">{file ? file.name : 'Click or drag PDF here'}</p>
            <p className="text-sm text-gray-500">Supports PDF files up to 10MB</p>
          </div>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="w-full border border-gray-300 rounded-lg shadow-sm p-3 bg-white focus:outline-none focus:ring-2 focus:ring-navy-blue">
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
              <input type="number" min="1" max="25" value={numQuestions} onChange={(e) => setNumQuestions(e.target.value)} className="w-full border border-gray-300 rounded-lg shadow-sm p-3 bg-white focus:outline-none focus:ring-2 focus:ring-navy-blue" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Time Limit (Mins)</label>
              <input type="number" min="1" max="120" value={timeLimit} onChange={(e) => setTimeLimit(e.target.value)} className="w-full border border-gray-300 rounded-lg shadow-sm p-3 bg-white focus:outline-none focus:ring-2 focus:ring-navy-blue" />
            </div>
          </div>

          <div className="mt-8 flex justify-center">
            <button
              onClick={startGeneration}
              disabled={!file}
              className={`px-8 py-3 rounded-full font-bold text-white shadow-sm transition-all ${
                file ? 'bg-india-green hover:bg-opacity-90' : 'bg-gray-300 cursor-not-allowed'
              }`}
            >
              Generate Practice Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'loading') {
    return (
      <div className="min-h-screen bg-light-bg pt-24 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-16 h-16 border-4 border-navy-blue border-t-india-saffron rounded-full animate-spin mb-6"></div>
          <h2 className="text-2xl font-bold text-navy-blue mb-2">Analyzing your PDF...</h2>
          <p className="text-gray-600">Extracting key concepts and building AI questions. This takes a few moments.</p>
        </div>
      </div>
    );
  }

  if (step === 'active') {
    const question = questions[currentQuestionIdx];
    return (
      <div className="min-h-screen bg-light-bg pt-24 px-4 pb-12">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <div className="bg-white rounded-2xl p-6 shadow-sm mb-6 flex justify-between items-center border border-gray-100">
            <div>
              <p className="text-sm text-gray-500 font-medium uppercase tracking-wider mb-1">Question {currentQuestionIdx + 1} of {questions.length}</p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2 w-48">
                <div className="bg-india-saffron h-2 rounded-full" style={{ width: `${((currentQuestionIdx) / questions.length) * 100}%` }}></div>
              </div>
            </div>
            <div className="text-2xl font-mono font-bold text-navy-blue bg-blue-50 px-4 py-2 rounded-lg">
              {formatTime(timeRemaining)}
            </div>
          </div>

          {/* Question */}
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
            <h2 className="text-xl md:text-2xl font-bold text-gray-900 mb-8 leading-relaxed">
              {question.question}
            </h2>

            <div className="space-y-4">
              {question.options.map((opt, i) => (
                <button
                  key={i}
                  onClick={() => handleOptionSelect(i)}
                  className={`w-full text-left p-4 rounded-xl border-2 transition-all flex items-center ${
                    selectedOptions[currentQuestionIdx] === i 
                      ? 'border-navy-blue bg-blue-50 font-bold text-navy-blue' 
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  <span className="w-8 h-8 rounded-full border border-current flex items-center justify-center mr-4 flex-shrink-0">
                    {String.fromCharCode(65 + i)}
                  </span>
                  {opt}
                </button>
              ))}
            </div>

            <div className="mt-10 flex justify-end">
              <button
                onClick={handleNext}
                disabled={selectedOptions[currentQuestionIdx] === undefined}
                className={`px-8 py-3 rounded-full font-bold text-white transition-all ${
                  selectedOptions[currentQuestionIdx] !== undefined 
                    ? 'bg-navy-blue hover:bg-opacity-90 shadow-md' 
                    : 'bg-gray-300 cursor-not-allowed'
                }`}
              >
                {currentQuestionIdx === questions.length - 1 ? 'Finish Quiz' : 'Next Question'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'result') {
    return (
      <div className="min-h-screen bg-light-bg pt-20 px-4 pb-12">
        <div className="max-w-3xl mx-auto">
          {/* Summary Card */}
          <div className="bg-white rounded-3xl p-10 shadow-sm border border-gray-100 text-center mb-8 relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-4 bg-gradient-to-r from-india-saffron via-navy-blue to-india-green"></div>
            <h1 className="text-3xl font-bold text-navy-blue mb-2 mt-4">Quiz Completed!</h1>
            <p className="text-gray-600 mb-8">You finished practicing from <span className="font-semibold text-gray-800">{file?.name}</span></p>

            <div className="inline-flex flex-col items-center justify-center w-40 h-40 rounded-full border-8 border-blue-50 bg-white shadow-inner mb-6">
              <span className="text-5xl font-black text-navy-blue">{quizScore}</span>
              <span className="text-gray-500 font-medium">out of {questions.length}</span>
            </div>

            <div className="flex justify-center mt-6">
              <button onClick={() => navigate('/dashboard')} className="px-8 py-3 bg-navy-blue text-white rounded-full font-bold hover:bg-opacity-90 shadow-md transition-all">
                Save to Dashboard
              </button>
            </div>
          </div>

          {/* Answer Review */}
          <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4 px-2">Answer Review</h3>
            {questions.map((q, idx) => {
              const uans = selectedOptions[idx];
              const cans = q.correctAnswer;
              const isCorrect = uans === cans;

              return (
                <div key={idx} className={`bg-white rounded-2xl p-6 shadow-sm border-l-8 ${isCorrect ? 'border-l-india-green' : 'border-l-red-500'}`}>
                  <div className="flex items-start">
                    <div className="mr-4 mt-1">
                      {isCorrect ? <CheckCircle className="w-6 h-6 text-india-green" /> : <XCircle className="w-6 h-6 text-red-500" />}
                    </div>
                    <div className="flex-1">
                      <p className="font-bold text-gray-900 mb-4 text-lg">{q.question}</p>
                      
                      <div className="mb-4 bg-gray-50 rounded-xl p-4">
                        <p className="text-sm font-semibold text-gray-500 uppercase mb-2">Options</p>
                        <ul className="space-y-2 text-sm text-gray-700">
                          {q.options.map((opt, i) => (
                            <li key={i} className={`flex items-center ${i === cans ? 'font-bold text-india-green' : i === uans ? 'font-bold text-red-500' : ''}`}>
                              <span className="w-5 h-5 rounded flex items-center justify-center mr-2 bg-gray-200 text-xs font-mono">{String.fromCharCode(65+i)}</span>
                              {opt}
                              {i === cans && <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">Correct</span>}
                              {i === uans && i !== cans && <span className="ml-2 text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">Your answer</span>}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <div className="bg-blue-50 rounded-xl p-4 text-sm text-navy-blue">
                        <p className="font-bold mb-1 border-b border-blue-200 pb-1">Explanation:</p>
                        <p>{q.explanation || 'No explanation provided.'}</p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default PracticeQuiz;
