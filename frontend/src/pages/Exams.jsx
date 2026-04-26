import { useState } from 'react';
import { Search, Calendar } from 'lucide-react';
import { Link } from 'react-router-dom';
import { centralCategories, stateCategories, examsData } from '../data/examsData';

const Exams = () => {
  const [activeTab, setActiveTab] = useState('central'); // 'central' or 'state'
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Get active categories based on tab
  const activeCategories = activeTab === 'central' ? centralCategories : stateCategories;

  // Filter exams
  const filteredExams = examsData.filter(exam => {
    // 1. Filter by level (Central or State)
    if (exam.level !== activeTab) return false;
    
    // 2. Filter by category
    if (categoryFilter && exam.category !== categoryFilter) return false;
    
    // 3. Filter by search term
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return exam.name.toLowerCase().includes(searchLower) || 
             exam.conductingBody.toLowerCase().includes(searchLower);
    }
    
    return true;
  });

  return (
    <div className="min-h-screen bg-light-bg pt-20 px-4 sm:px-6 lg:px-8 pb-12">
      <div className="max-w-7xl mx-auto py-8">
        
        {/* Header & Search */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 space-y-4 md:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-navy-blue">Exam Directory</h1>
            <p className="text-gray-600 mt-1">Find your next target examination</p>
          </div>
          
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input 
              type="text" 
              placeholder="Search exams..." 
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-xl w-full focus:ring-2 focus:ring-navy-blue focus:border-transparent outline-none transition-shadow shadow-sm"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {/* Top-Level Tabs */}
        <div className="flex space-x-8 mb-6 border-b border-gray-200">
          <button
            onClick={() => { setActiveTab('central'); setCategoryFilter(''); }}
            className={`pb-3 text-lg font-semibold transition-all relative ${
              activeTab === 'central' 
                ? 'text-navy-blue border-b-2 border-navy-blue' 
                : 'text-gray-500 hover:text-gray-800'
            }`}
          >
            Central Exams
          </button>
          <button
            onClick={() => { setActiveTab('state'); setCategoryFilter(''); }}
            className={`pb-3 text-lg font-semibold transition-all relative ${
              activeTab === 'state' 
                ? 'text-navy-blue border-b-2 border-navy-blue' 
                : 'text-gray-500 hover:text-gray-800'
            }`}
          >
            State Exams (Tamil Nadu)
          </button>
        </div>

        {/* Category Tabs / Chips */}
        <div className="mb-10 overflow-x-auto pb-2 scrollbar-hide">
          <div className="flex space-x-2">
            <button
              onClick={() => setCategoryFilter('')}
              className={`px-5 py-2 rounded-full text-sm font-semibold transition-all whitespace-nowrap border ${
                categoryFilter === '' 
                ? 'bg-navy-blue text-white border-navy-blue shadow-md' 
                : 'bg-white text-gray-600 border-gray-200 hover:border-navy-blue/30 hover:bg-gray-50'
              }`}
            >
              All Exams
            </button>
            {activeCategories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setCategoryFilter(cat.slug)}
                className={`px-5 py-2 rounded-full text-sm font-semibold transition-all whitespace-nowrap border ${
                  categoryFilter === cat.slug 
                  ? 'bg-navy-blue text-white border-navy-blue shadow-md' 
                  : 'bg-white text-gray-600 border-gray-200 hover:border-navy-blue/30 hover:bg-gray-50'
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        {/* Exams Grid */}
        {filteredExams.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-3xl border border-gray-100 shadow-sm">
            <div className="bg-gray-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
               <Search className="text-gray-300 w-10 h-10" />
            </div>
            <h3 className="text-2xl font-bold text-gray-800">No exams available</h3>
            <p className="text-gray-500 mt-2 max-w-xs mx-auto">We couldn't find any exams matching your criteria. Try adjusting your filters!</p>
            <button 
              onClick={() => {setCategoryFilter(''); setSearchTerm('');}}
              className="mt-6 text-navy-blue font-semibold hover:underline"
            >
              Clear filters
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredExams.map((exam) => {
              const categoryMatch = activeCategories.find(c => c.slug === exam.category);
              const categoryName = categoryMatch ? categoryMatch.name : exam.category;
              
              return (
              <div key={exam.key} className="group bg-white rounded-3xl p-7 shadow-sm border border-gray-100 hover:shadow-xl transition-all duration-300 flex flex-col relative overflow-hidden">
                {/* Status Badge */}
                <div className="absolute top-0 right-0">
                  <span className={`px-4 py-1.5 rounded-bl-2xl text-[10px] uppercase font-bold tracking-wider ${
                    exam.status === 'Open' ? 'bg-green-100 text-green-700' : 
                    exam.status === 'Upcoming' ? 'bg-blue-100 text-blue-700' : 
                    'bg-red-100 text-red-700'
                  }`}>
                    {exam.status || 'Upcoming'}
                  </span>
                </div>

                <div className="flex flex-col mb-6">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1 truncate">
                    {categoryName}
                  </span>
                  <h3 className="text-2xl font-bold text-navy-blue leading-tight group-hover:text-india-saffron transition-colors">
                    {exam.name}
                  </h3>
                </div>
                
                <div className="space-y-3 mb-8">
                  <p className="text-sm text-gray-600 flex items-start">
                    <span className="font-bold text-gray-800 min-w-[100px] inline-block">Conducted by:</span> 
                    <span className="flex-1">{exam.conductingBody}</span>
                  </p>
                  <p className="text-sm text-gray-600 flex items-center">
                    <span className="font-bold text-gray-800 min-w-[100px] inline-block">Expected:</span> 
                    <span className="flex-1 font-bold text-india-saffron flex items-center">
                      <Calendar className="w-4 h-4 mr-1"/> {exam.expectedMonth || 'TBA'}
                    </span>
                  </p>
                </div>

                <div className="mt-auto grid grid-cols-2 gap-4">
                  <Link 
                    to={`/exams/${exam.key}`}
                    className="flex items-center justify-center px-3 py-2.5 rounded-xl border border-navy-blue text-navy-blue text-sm font-bold hover:bg-blue-50 transition-colors truncate"
                  >
                    View Syllabus
                  </Link>
                  
                  {exam.is_open ? (
                    <a 
                      href={exam.apply_link || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center px-4 py-2.5 rounded-xl bg-india-green text-white text-sm font-bold hover:bg-green-700 transition-all shadow-md shadow-green-200"
                    >
                      Apply Link
                    </a>
                  ) : (
                    <button 
                      disabled
                      className="flex items-center justify-center px-4 py-2.5 rounded-xl bg-gray-100 text-gray-400 text-sm font-bold cursor-not-allowed"
                    >
                      {exam.status === 'Upcoming' ? 'Opening Soon' : 'Closed'}
                    </button>
                  )}
                </div>
              </div>
            )})}
          </div>
        )}
      </div>
    </div>
  );
};

export default Exams;
