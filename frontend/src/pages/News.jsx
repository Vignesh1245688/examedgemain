import { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import { Clock, ExternalLink, Globe } from 'lucide-react';

const News = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('news/');
      setNews(res.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch news', err);
      setError('No data available');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-light-bg pt-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto py-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 space-y-4 md:space-y-0">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-3xl font-bold text-navy-blue">Exam News</h1>
              <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded animate-pulse">
                LIVE
              </span>
            </div>
            <p className="text-gray-600 mt-1 flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              Last Updated: {lastUpdated.toLocaleTimeString()}
            </p>
          </div>
          
          <button 
            onClick={fetchNews}
            disabled={loading}
            className="px-4 py-2 bg-navy-blue text-white rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh News'}
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-navy-blue"></div>
          </div>
        ) : error ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm">
            <h3 className="text-xl font-semibold text-gray-700">{error}</h3>
            <p className="text-gray-500 mt-2">Could not fetch live updates. Please try again later.</p>
          </div>
        ) : news.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-100 shadow-sm">
            <h3 className="text-xl font-semibold text-gray-700">No news available currently</h3>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {news.map((item, index) => (
              <div key={index} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-all flex flex-col pt-8">
                <div className="flex justify-between items-start mb-4">
                  <span className="px-3 py-1 bg-blue-50 text-navy-blue text-xs font-semibold rounded-full border border-blue-100 whitespace-nowrap flex items-center">
                    <Globe className="w-3 h-3 mr-1" />
                    {item.source || 'News'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(item.published_date).toLocaleDateString()}
                  </span>
                </div>
                
                <h3 className="text-xl font-bold text-navy-blue line-clamp-2 mb-2">{item.title}</h3>
                
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {item.description}
                </p>

                <div className="mt-auto pt-4 border-t border-gray-50">
                  <a 
                    href={item.article_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-india-green hover:text-green-700 font-medium text-sm flex items-center transition-colors"
                  >
                    Read More <ExternalLink className="w-4 h-4 ml-1" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
};

export default News;
