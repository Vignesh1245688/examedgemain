import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class NewsAPIView(APIView):
    def get(self, request):
        api_key = os.environ.get('NEWS_API_KEY', 'YOUR_NEWS_API_KEY')
        # 1. Try to fetch from NewsAPI.ai (Event Registry) if key is present
        if api_key and api_key != 'YOUR_NEWS_API_KEY':
            url = "https://eventregistry.org/api/v1/article/getArticles"
            params = {
                "action": "getArticles",
                "keyword": "UPSC",
                "articlesPage": 1,
                "articlesCount": 10,
                "articlesSortBy": "date",
                "articlesSortByAsc": "false",
                "resultType": "articles",
                "apiKey": api_key,
                "lang": "eng"
            }
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                articles = data.get("articles", {}).get("results", [])
                
                if articles:
                    news_data = []
                    for article in articles:
                        news_data.append({
                            "title": article.get("title"),
                            "description": article.get("body", "")[:200] + "..." if article.get("body") else "",
                            "source": article.get("source", {}).get("title"),
                            "published_date": article.get("dateTime"),
                            "article_url": article.get("url"),
                        })
                    return Response(news_data, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"NewsAPI.ai Fetch Error: {e}")
                # Fall through to mock data
        
        # 2. Fallback to mock data
        mock_news = [
            {
                "title": "SSC CGL 2024 Notification Released",
                "description": "The Staff Selection Commission has officially released the notification for the Combined Graduate Level Examination 2024. Read the full details here.",
                "source": "Staff Selection Commission",
                "published_date": "2024-06-24T10:00:00Z",
                "article_url": "https://ssc.nic.in"
            },
            {
                "title": "UPSC Prelims Result Declared",
                "description": "Union Public Service Commission has declared the results for the CSE Civil Services Preliminary Examination. Candidates can check their scores online.",
                "source": "UPSC Official",
                "published_date": "2024-06-12T14:30:00Z",
                "article_url": "https://upsc.gov.in"
            },
            {
                "title": "Railway Recruitment: 1.5 Lakh Vacancies Announced",
                "description": "The Railway Recruitment Board (RRB) has announced widespread hiring across various zones to meet operational demands.",
                "source": "Ministry of Railways",
                "published_date": "2024-05-30T09:15:00Z",
                "article_url": "https://indianrailways.gov.in"
            }
        ]
        return Response(mock_news, status=status.HTTP_200_OK)
