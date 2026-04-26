import os
import tempfile
import pdfplumber
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .models import PracticeQuizResult
from .serializers import PracticeQuizResultSerializer

class GenerateQuizView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        difficulty = request.data.get('difficulty', 'Medium')
        num_questions = request.data.get('num_questions', '5')
        try:
            num_questions = int(num_questions)
        except ValueError:
            num_questions = 5

        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Save file temporarily to read it with pdfplumber
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in file_obj.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            # Extract text
            text = ""
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            
            os.remove(tmp_path)

            if not text.strip():
                return Response({'error': 'Could not extract text from the PDF'}, status=status.HTTP_400_BAD_REQUEST)

            # limit text length for API
            text = text[:15000]

            questions = self.generate_questions_ai(text, difficulty, num_questions)
            
            return Response({'questions': questions}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_questions_ai(self, text, difficulty, num_questions):
        prompt = f"""Generate {num_questions} multiple choice questions based on the following text. 
The difficulty level should be {difficulty}.
Return the output STRICTLY as a JSON array where each object has:
- question: the question string
- options: an array of 4 option strings
- correctAnswer: the integer index (0-3) of the correct option
- explanation: a short explanation of why it is correct

IMPORTANT: Return ONLY the JSON array, no other text or markdown formatting.

Text:
{text}
"""
        
        # Try Groq with Llama 3.3 70B
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            try:
                from groq import Groq

                client = Groq(api_key=groq_api_key)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful quiz generator. Always respond with valid JSON arrays only, no markdown formatting or extra text."
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=4096,
                )
                
                # Parse the response
                raw = chat_completion.choices[0].message.content
                
                # Clean up any markdown formatting
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0]
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0]
                    
                data = json.loads(raw.strip())
                if isinstance(data, list) and len(data) > 0:
                    return data
            except Exception as e:
                print(f"Groq/Llama error: {e}")

        # Fallback: Try Gemini if Groq fails
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                from google import genai

                client = genai.Client(api_key=gemini_api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                
                raw = response.text
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0]
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0]
                    
                data = json.loads(raw.strip())
                if isinstance(data, list) and len(data) > 0:
                    return data
            except Exception as e:
                print(f"Gemini fallback error: {e}")

        # Fallback dummy questions
        return [
            {
                "question": "What is the main topic of the uploaded document?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correctAnswer": 0,
                "explanation": "This is a placeholder question generated because no valid API key was found or an error occurred."
            },
            {
                "question": "Which of the following is true based on the text?",
                "options": ["Fact 1", "Fact 2", "Fact 3", "Fact 4"],
                "correctAnswer": 1,
                "explanation": "Dummy explanation."
            }
        ]

class SaveQuizResultView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PracticeQuizResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        results = PracticeQuizResult.objects.filter(user=request.user).order_by('-created_at')
        serializer = PracticeQuizResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
