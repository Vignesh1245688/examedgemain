import os
import re
import requests
from urllib.parse import quote_plus, unquote
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class VideoResourceAPIView(APIView):
    def get(self, request):
        query = request.query_params.get("q", "UPSC preparation")
        api_key = os.environ.get("YOUTUBE_API_KEY", "")

        # Try live fetch
        if api_key and api_key != 'YOUR_YOUTUBE_API_KEY' and api_key != 'YOUR_YOUTUBE_KEY_HERE':
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": 10,
                "key": api_key
            }
            try:
                res = requests.get(url, params=params, timeout=5)
                res.raise_for_status()
                data = res.json()
                videos = []
                for item in data.get("items", []):
                    snippet = item.get("snippet", {})
                    video_id = item.get("id", {}).get("videoId")
                    videos.append({
                        "title": snippet.get("title"),
                        "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                        "channel_name": snippet.get("channelTitle"),
                        "video_link": f"https://www.youtube.com/watch?v={video_id}" if video_id else None
                    })
                if videos:
                    return Response(videos, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"YouTube API Error: {e}")

        # Fallback to mock videos
        mock_videos = [
            {
                "title": f"Complete {query} Strategy 2024",
                "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                "channel_name": "Exam Prep Masters",
                "video_link": "https://youtube.com/watch?v=dQw4w9WgXcQ"
            },
            {
                "title": f"Top 10 Tips for {query}",
                "thumbnail": "https://i.ytimg.com/vi/jNQXAC9IVRw/hqdefault.jpg",
                "channel_name": "Study With Me",
                "video_link": "https://youtube.com/watch?v=jNQXAC9IVRw"
            },
            {
                "title": f"Must Read Books for {query}",
                "thumbnail": "https://i.ytimg.com/vi/P-3GOo_nWoc/hqdefault.jpg",
                "channel_name": "Topper's Talk",
                "video_link": "https://youtube.com/watch?v=P-3GOo_nWoc"
            }
        ]
        return Response(mock_videos, status=status.HTTP_200_OK)


class PDFResourceAPIView(APIView):
    """
    Fetches PDF study materials using DuckDuckGo live search.
    No API key required - returns real, direct links to study resources.
    """
    def get(self, request):
        query = request.query_params.get("q", "UPSC notes PDF")
        
        # Clean and enhance the query for better study material results
        base_query = query.replace(" notes PDF", "").replace(" PDF", "").replace(" preparation", "").strip()
        search_query = f"{base_query} study material notes PDF free download"
        
        # Live search using DuckDuckGo (free, no API key needed)
        try:
            from ddgs import DDGS
            
            results = DDGS().text(search_query, max_results=15)
            
            pdfs = []
            seen_urls = set()
            
            for result in results:
                link = result.get("href", "")
                title = result.get("title", "")
                snippet = result.get("body", "")
                
                if link and link not in seen_urls:
                    seen_urls.add(link)
                    pdfs.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
            
            if pdfs:
                return Response(pdfs[:10], status=status.HTTP_200_OK)
                
        except Exception as e:
            print(f"DuckDuckGo Search Error: {e}")

        # Fallback: return helpful message
        fallback = [
            {
                "title": f"Search for {base_query} study material",
                "link": f"https://duckduckgo.com/?q={base_query}+study+material+notes+PDF",
                "snippet": f"Click here to search for {base_query} study materials on DuckDuckGo."
            }
        ]
        return Response(fallback, status=status.HTTP_200_OK)
