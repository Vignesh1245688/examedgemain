import { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { BookOpen } from 'lucide-react'; // Placeholder Logo Icon
import NotificationDropdown from './NotificationDropdown';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="fixed w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <BookOpen className="h-8 w-8 text-navy-blue" />
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-navy-blue to-india-saffron">
              ExamEdge
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex flex-1 items-center justify-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-navy-blue font-medium transition-colors">Home</Link>
            <Link to="/exams" className="text-gray-700 hover:text-navy-blue font-medium transition-colors">Exams</Link>
            <Link to="/groups" className="text-gray-700 hover:text-navy-blue font-medium transition-colors">Groups</Link>
            <Link to="/resources" className="text-gray-700 hover:text-navy-blue font-medium transition-colors">Resources</Link>
            <Link to="/news" className="text-gray-700 hover:text-navy-blue font-medium transition-colors">News</Link>
          </div>

          {/* Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <>
                <NotificationDropdown />
                <Link to="/dashboard" className="text-gray-700 hover:text-navy-blue font-medium transition-colors">Dashboard</Link>
                <button 
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors font-medium"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-gray-700 hover:text-navy-blue font-medium transition-colors">Login</Link>
                <Link 
                  to="/register" 
                  className="px-6 py-2 rounded-full bg-navy-blue text-white hover:bg-opacity-90 transition-all font-medium shadow-sm shadow-navy-blue/30"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
