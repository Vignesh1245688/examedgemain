import { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { Search, FileText, Video, ExternalLink, RefreshCw } from 'lucide-react';

const Resources = () => {
  const [videos, setVideos] = useState([]);
  const [pdfs, setPdfs] = useState([]);
  const [loadingVideos, setLoadingVideos] = useState(true);
  const [loadingPdfs, setLoadingPdfs] = useState(true);
  const [videoError, setVideoError] = useState(null);
  const [pdfError, setPdfError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('UPSC');
  const [activeTab, setActiveTab] = useState('VIDEOS'); // 'VIDEOS' or 'PDFS'

  useEffect(() => {
    fetchVideos();
    fetchPdfs();
    // eslint-disable-next-line
  }, []);

  const fetchVideos = async (query = searchTerm) => {
    try {
      setLoadingVideos(true);
      setVideoError(null);
      const res = await api.get(`resources/videos/?q=${query} preparation`);
      setVideos(res.data);
    } catch (err) {
      console.error('Video fetch error:', err);
      setVideoError('No data available');
    } finally {
      setLoadingVideos(false);
    }
  };

  const fetchPdfs = async (query = searchTerm) => {
    try {
      setLoadingPdfs(true);
      setPdfError(null);
      const res = await api.get(`resources/pdfs/?q=${query} notes PDF`);
      setPdfs(res.data);
    } catch (err) {
      console.error('PDF fetch error:', err);
      setPdfError('No data available');
    } finally {
      setLoadingPdfs(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (activeTab === 'VIDEOS') fetchVideos(searchTerm);
    else fetchPdfs(searchTerm);
  };

  return (
    <div className="min-h-screen bg-light-bg pt-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto py-8">

        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 space-y-4 md:space-y-0">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-navy-blue">Live Resources</h1>
              <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded animate-pulse">
                LIVE
              </span>
            </div>
            <p className="text-gray-600 mt-1">Real-time curated videos and study website for free pdf download</p>
          </div>

          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 w-full md:w-auto">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
              <input
                type="text"
                placeholder="Search topic..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full sm:w-64 focus:ring-2 focus:ring-navy-blue focus:border-transparent outline-none transition-shadow"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button
              type="submit"
              className="flex items-center justify-center px-4 py-2 bg-navy-blue text-white rounded-lg hover:bg-opacity-90 transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" /> Refresh
            </button>
          </form>
        </div>

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            className={`pb-3 px-4 text-sm font-medium ${activeTab === 'VIDEOS' ? 'border-b-2 border-navy-blue text-navy-blue' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setActiveTab('VIDEOS')}
          >
            Video Resources
          </button>
          <button
            className={`pb-3 px-4 text-sm font-medium ${activeTab === 'PDFS' ? 'border-b-2 border-navy-blue text-navy-blue' : 'text-gray-500 hover:text-gray-700'}`}
            onClick={() => setActiveTab('PDFS')}
          >
            Reference Sites
          </button>
        </div>

        {/* Videos Section */}
        {activeTab === 'VIDEOS' && (
          <div>
            {loadingVideos ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse bg-white p-6 rounded-2xl shadow-sm border border-gray-100 h-64"></div>
                ))}
              </div>
            ) : videoError ? (
              <div className="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm">
                <Video className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700">{videoError}</h3>
              </div>
            ) : videos.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm">
                <Video className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700">No videos found</h3>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {videos.map((video, idx) => (
                  <div key={idx} className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 hover:shadow-md transition-all flex flex-col">
                    {video.thumbnail && (
                      <img src={video.thumbnail} alt={video.title} className="w-full h-40 object-cover" />
                    )}
                    <div className="p-4 flex flex-col flex-1">
                      <h3 className="text-md font-bold text-gray-900 mb-1 line-clamp-2">{video.title}</h3>
                      <p className="text-sm text-gray-500 mb-4">{video.channel_name}</p>

                      <div className="mt-auto pt-4 border-t border-gray-50">
                        <a
                          href={video.video_link}
                          target="_blank"
                          rel="noreferrer"
                          className="text-navy-blue hover:text-blue-700 font-medium text-sm flex items-center transition-colors"
                        >
                          Watch Video <ExternalLink className="w-4 h-4 ml-1" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* PDFs Section */}
        {activeTab === 'PDFS' && (
          <div>
            {loadingPdfs ? (
              <div className="flex flex-col space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-24"></div>
                ))}
              </div>
            ) : pdfError ? (
              <div className="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700">{pdfError}</h3>
              </div>
            ) : pdfs.length === 0 ? (
              <div className="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700">No PDFs found</h3>
              </div>
            ) : (
              <div className="flex flex-col space-y-4">
                {pdfs.map((pdf, idx) => (
                  <div key={idx} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-all flex items-start justify-between">
                    <div className="flex-1 pr-4">
                      <div className="flex items-center space-x-2 mb-2">
                        <FileText className="w-5 h-5 text-red-500" />
                        <h3 className="text-lg font-bold text-gray-900 line-clamp-1">{pdf.title}</h3>
                      </div>
                      <p className="text-sm text-gray-600 line-clamp-2">{pdf.snippet}</p>
                    </div>
                    <a
                      href={pdf.link}
                      target="_blank"
                      rel="noreferrer"
                      className="whitespace-nowrap px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 font-medium text-sm flex items-center transition-colors"
                    >
                      View site <ExternalLink className="w-4 h-4 ml-1" />
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
};

export default Resources;
