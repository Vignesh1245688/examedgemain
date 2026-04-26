import { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { BookOpen, ShieldCheck, Target, Zap, ChevronRight, FileText } from 'lucide-react';

const Home = () => {
  const { user } = useContext(AuthContext);

  const features = [
    {
      title: 'Comprehensive Directory',
      description: 'Find dates, syllabus, and eligibility for all major Indian competitive exams in one place.',
      icon: <BookOpen className="w-8 h-8 text-india-saffron" />,
    },
    {
      title: 'Real-Time Updates',
      description: 'Get notified about application starts, admit cards, and results instantly.',
      icon: <Zap className="w-8 h-8 text-india-green" />,
    },
    {
      title: 'Mock Tests & Quizzes',
      description: 'Practice with timer-based tests covering History, Polity, Geography, and Current Affairs.',
      icon: <Target className="w-8 h-8 text-navy-blue" />,
    },
    {
      title: 'Verified Resources',
      description: 'Access curated PDFs, notes, and video lectures to boost your preparation.',
      icon: <ShieldCheck className="w-8 h-8 text-india-saffron" />,
    },
  ];

  return (
    <div className="min-h-screen bg-light-bg pt-16">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-32">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-light-bg to-blue-50 -z-10" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold text-navy-blue tracking-tight leading-tight mb-6">
            An Exam Platform That <br className="hidden md:block"/>
            <span className="text-india-saffron">Empowers Your Journey</span>
          </h1>
          <p className="max-w-2xl mx-auto text-xl text-gray-600 mb-10">
            Unlock real-time notifications, comprehensive exam directories, and structured study resources for UPSC, SSC, Banking, and State Exams.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-6">
            {!user ? (
              <Link to="/register" className="px-8 py-3 bg-navy-blue text-white rounded-full font-semibold hover:bg-opacity-90 transition-all shadow-lg shadow-navy-blue/30 flex items-center">
                Join Now <ChevronRight className="ml-2 w-5 h-5" />
              </Link>
            ) : (
              <Link to="/dashboard" className="px-8 py-3 bg-india-green text-white rounded-full font-semibold hover:bg-opacity-90 transition-all shadow-lg shadow-india-green/30 flex items-center">
                Go to Dashboard <ChevronRight className="ml-2 w-5 h-5" />
              </Link>
            )}
            <Link to="/exams" className="px-8 py-3 bg-white text-navy-blue border border-gray-200 rounded-full font-semibold hover:border-gray-300 transition-all shadow-sm">
              Explore Exams
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-navy-blue mb-4">
              The Future of Preparation is Here – <br className="hidden md:block"/>
              And It's <span className="text-india-saffron">Smarter</span> Than Ever
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, idx) => (
              <div key={idx} className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow group cursor-pointer">
                <div className="mb-6 p-4 bg-gray-50 rounded-xl inline-block group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Step by Step Section */}
      <section className="py-24 bg-light-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-navy-blue mb-4">
              Understanding How It Works <br/>
              <span className="text-india-green">Step by Step</span>
            </h2>
          </div>

          <div className="flex flex-col md:flex-row justify-center items-start space-y-12 md:space-y-0 md:space-x-12 relative">
            {/* Connecting Line */}
            <div className="hidden md:block absolute top-8 left-1/6 right-1/6 h-0.5 bg-gray-200 -z-10" />

            <div className="flex-1 text-center relative z-10">
              <div className="w-16 h-16 mx-auto bg-navy-blue text-white rounded-full flex items-center justify-center text-2xl font-bold mb-6 mx-auto shadow-md">
                1
              </div>
              <h3 className="text-xl font-bold mb-2">Find Your Target</h3>
              <p className="text-gray-600 text-sm">Browse our directory and bookmark exams you want to track.</p>
            </div>

            <div className="flex-1 text-center relative z-10">
              <div className="w-16 h-16 mx-auto bg-india-saffron text-white rounded-full flex items-center justify-center text-2xl font-bold mb-6 mx-auto shadow-md">
                2
              </div>
              <h3 className="text-xl font-bold mb-2">Track & Notify</h3>
              <p className="text-gray-600 text-sm">Get instant alerts for application dates and syllabus changes.</p>
            </div>

            <div className="flex-1 text-center relative z-10">
              <div className="w-16 h-16 mx-auto bg-india-green text-white rounded-full flex items-center justify-center text-2xl font-bold mb-6 mx-auto shadow-md">
                3
              </div>
              <h3 className="text-xl font-bold mb-2">Practice & Pass</h3>
              <p className="text-gray-600 text-sm">Use our quiz module and PDF resources to ace the exam.</p>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};

export default Home;
