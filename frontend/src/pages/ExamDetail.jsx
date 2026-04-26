import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getExamByKey } from '../data/examsData';
import { Calendar, FileText, CheckCircle, ExternalLink, Bookmark, ArrowLeft, Building2 } from 'lucide-react';

const ExamDetail = () => {
  const { id } = useParams();
  const [exam, setExam] = useState(null);
  const [isBookmarked, setIsBookmarked] = useState(false);

  useEffect(() => {
    // Scroll to top on load
    window.scrollTo(0, 0);
    // Fetch from static JSON
    const foundExam = getExamByKey(id);
    setExam(foundExam);
  }, [id]);

  const toggleBookmark = () => {
    setIsBookmarked(!isBookmarked);
  };

  if (!exam) return (
    <div className="pt-32 min-h-screen flex flex-col items-center bg-light-bg text-center">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">Exam not found</h2>
      <p className="text-gray-500 mb-6">The exam you are looking for does not exist or has been removed.</p>
      <Link to="/exams" className="px-6 py-2 bg-navy-blue text-white rounded-xl hover:bg-blue-800 transition-colors">
        Back to Directory
      </Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-light-bg pt-20 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        
        {/* Back Link */}
        <Link to="/exams" className="inline-flex items-center text-gray-500 hover:text-navy-blue mb-6 transition-colors font-medium">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Exams
        </Link>
        
        {/* Header Section */}
        <div className="bg-white rounded-3xl p-8 sm:p-10 shadow-sm border border-gray-100 mb-8 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-2 h-full bg-india-saffron"></div>
          
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
            <div className="mb-6 md:mb-0">
              <span className="px-3 py-1 bg-blue-50 text-navy-blue text-xs font-bold uppercase tracking-wider rounded-full border border-blue-100 mb-4 inline-block">
                {exam.category.replace('-', ' ')}
              </span>
              <h1 className="text-3xl sm:text-4xl font-extrabold text-navy-blue mb-3">{exam.name}</h1>
              <div className="flex items-center text-gray-600">
                <Building2 className="w-5 h-5 mr-2 text-gray-400" />
                <span><span className="font-medium text-gray-800">Conducted by:</span> {exam.conductingBody}</span>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 shrink-0">
              <button
                onClick={toggleBookmark}
                className={`flex items-center justify-center px-6 py-3 rounded-xl font-medium transition-all ${
                  isBookmarked 
                    ? 'bg-india-saffron/10 text-india-saffron border border-india-saffron/20' 
                    : 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 shadow-sm'
                }`}
              >
                <Bookmark className={`w-5 h-5 mr-2 ${isBookmarked ? 'fill-current' : ''}`} />
                {isBookmarked ? 'Saved' : 'Save'}
              </button>

              {exam.is_open ? (
                <a 
                  href={exam.apply_link || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center px-8 py-3 rounded-xl bg-india-green text-white font-bold hover:bg-green-700 transition-all shadow-md shadow-green-200"
                >
                  Apply Now <ExternalLink className="w-4 h-4 ml-2" />
                </a>
              ) : (
                <div className="flex items-center justify-center px-8 py-3 rounded-xl bg-gray-100 text-gray-400 font-bold cursor-not-allowed border border-gray-200">
                  {exam.status === 'Upcoming' ? 'Opening Soon' : 'Applications Closed'}
                </div>
              )}
            </div>
          </div>
          
          <div className="mt-8 pt-6 border-t border-gray-50 flex flex-wrap gap-6 text-sm">
            {exam.official_link && (
              <a 
                href={exam.official_link || '#'} 
                target="_blank" 
                rel="noreferrer"
                className="inline-flex items-center text-navy-blue hover:text-blue-800 font-bold transition-colors"
              >
                Official Website <ExternalLink className="w-4 h-4 ml-1.5" />
              </a>
            )}
            
            <div className="flex items-center text-gray-500">
              <span className="font-semibold text-gray-700 mr-2">Est. Application Window:</span>
              {exam.application_start_date} to {exam.application_end_date}
            </div>
          </div>
        </div>

        {/* Info Grid */}
        <div className="grid md:grid-cols-4 gap-8">
          
          {/* Main Content Area */}
          <div className="md:col-span-3 space-y-8">
            
            {/* Overview / Eligibility Card */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
               <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                 <CheckCircle className="w-6 h-6 text-india-green mr-2" />
                 Eligibility & Overview
               </h2>
               <p className="text-gray-700 leading-relaxed mb-4">
                 {exam.description}
               </p>
               <div className="bg-gray-50 p-4 rounded-xl border border-gray-100">
                 <h4 className="font-semibold text-gray-800 mb-2">Basic Eligibility</h4>
                 <p className="text-gray-600 text-sm">{exam.eligibility || 'Not specified. Refer official notification.'}</p>
               </div>
            </div>

            {/* Detailed Table & Pattern Section */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
               <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                 <FileText className="w-7 h-7 text-navy-blue mr-3" />
                 Detailed Syllabus & Exam Pattern
               </h2>
               
               <p className="text-gray-700 leading-relaxed mb-8">
                 {exam.syllabus?.overview || 'Detailed syllabus will be updated soon.'}
               </p>

               {/* Exam Overview Summary */}
               <div className="bg-blue-50/60 border border-blue-100 p-6 rounded-2xl mb-8">
                 <h3 className="text-lg font-bold text-navy-blue mb-4">Pattern Overview</h3>
                 <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-6">
                   <div>
                     <span className="block text-sm text-gray-500 mb-1">Total Marks</span>
                     <span className="font-bold text-gray-900 text-xl">{exam.syllabus?.total_marks || 'N/A'}</span>
                   </div>
                   <div>
                     <span className="block text-sm text-gray-500 mb-1">Total Questions</span>
                     <span className="font-bold text-gray-900 text-xl">{exam.syllabus?.total_questions || 'N/A'}</span>
                   </div>
                   <div>
                     <span className="block text-sm text-gray-500 mb-1">Duration</span>
                     <span className="font-bold text-gray-900 text-xl">{exam.syllabus?.duration || 'N/A'}</span>
                   </div>
                 </div>
                 <div className="pt-4 border-t border-blue-200/60">
                   <span className="block text-sm text-gray-500 mb-2">Exam Pattern Notes</span>
                   <p className="text-gray-800 text-sm whitespace-pre-wrap leading-relaxed">{exam.syllabus?.pattern}</p>
                 </div>
               </div>

               {/* Detailed Subject / Topic Breakdown Table */}
               <h3 className="font-bold text-gray-800 text-lg mb-4">Subject-wise Mark Distribution</h3>
               <div className="overflow-x-auto shadow-sm border border-gray-200 rounded-xl">
                 <table className="min-w-full divide-y divide-gray-200">
                   <thead className="bg-gray-50">
                     <tr>
                       <th scope="col" className="px-5 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider w-[25%]">Subject</th>
                       <th scope="col" className="px-5 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider w-[25%]">Topic</th>
                       <th scope="col" className="px-5 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider w-[35%]">Subtopics</th>
                       <th scope="col" className="px-5 py-4 text-right text-xs font-bold text-gray-600 uppercase tracking-wider whitespace-nowrap w-[15%]">Marks Weightage</th>
                     </tr>
                   </thead>
                   <tbody className="bg-white divide-y divide-gray-200">
                     {exam.syllabus?.subjects?.map((subject, subjectIdx) => (
                       subject.topics?.map((topic, topicIdx) => (
                         <tr key={`${subjectIdx}-${topicIdx}`} className="hover:bg-gray-50 transition-colors">
                           <td className="px-5 py-4 text-sm font-semibold text-navy-blue align-top">
                             {topicIdx === 0 && (
                               <>
                                 <span className="block text-base">{subject.name}</span>
                                 {subject.total_subject_marks && (
                                   <span className="block text-xs text-gray-500 font-normal mt-1.5 bg-gray-100 inline-block px-2 py-1 rounded w-max">
                                     Total: {subject.total_subject_marks} Marks
                                   </span>
                                 )}
                               </>
                             )}
                           </td>
                           <td className="px-5 py-4 text-sm text-gray-900 font-medium align-top">
                             {topic.name}
                           </td>
                           <td className="px-5 py-4 text-sm text-gray-600 align-top">
                             <ul className="list-disc list-inside space-y-1">
                               {topic.subtopics?.map((sub, i) => <li key={i}>{sub}</li>)}
                             </ul>
                           </td>
                           <td className="px-5 py-4 text-sm font-bold text-india-saffron text-right whitespace-nowrap align-top">
                             {topic.marks_weightage}
                           </td>
                         </tr>
                       ))
                     ))}
                   </tbody>
                 </table>
               </div>

            </div>
          </div>

          {/* Sidebar */}
          <div className="md:col-span-1 space-y-6 md:space-y-8">
            
            {/* Quick Stats */}
            <div className="bg-gradient-to-br from-navy-blue to-blue-800 p-6 rounded-2xl shadow-md text-white relative overflow-hidden">
              <div className="absolute -right-6 -top-6 opacity-10">
                <Building2 className="w-32 h-32" />
              </div>
              <h3 className="text-lg font-bold mb-2 relative z-10">Vacancies / Openings</h3>
              <p className="text-3xl font-extrabold text-white relative z-10 flex items-baseline">
                {exam.vacancies || 'TBA'}
                <span className="text-base font-normal opacity-80 ml-2">Appx.</span>
              </p>
              <p className="text-blue-200 text-xs mt-3 opacity-80 relative z-10 leading-snug">
                Subject to change based on official notification mandate.
              </p>
            </div>

            {/* Dates Card */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-navy-blue mb-4 flex items-center pb-2 border-b border-gray-50">
                <Calendar className="w-5 h-5 mr-2 text-india-saffron" />
                Key Events
              </h3>
              
              {!exam.dates || exam.dates.length === 0 ? (
                <p className="text-sm text-gray-500 italic">No dates announced yet.</p>
              ) : (
                <ul className="space-y-4">
                  {exam.dates.map((dateObj) => (
                    <li key={dateObj.id} className="flex flex-col relative pl-4 border-l-2 border-india-saffron/30">
                      <div className="absolute w-2 h-2 rounded-full bg-india-saffron left-[-5px] top-1.5 hidden md:block"></div>
                      <span className="font-semibold text-gray-900 text-sm mb-0.5 leading-snug">{dateObj.date_type.replace('_', ' ')}</span>
                      <span className="text-gray-600 text-xs font-medium">{dateObj.date}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

          </div>

        </div>
      </div>
    </div>
  );
};

export default ExamDetail;
