import os, sys, django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from exams.models import Category, Exam, ExamDate
from resources.models import Resource
from quiz.models import Question
from news.models import NewsAlert
from datetime import date, timedelta

# ── CATEGORIES ──────────────────────────────────
categories_data = [
    {"name": "Central Govt", "slug": "central"},
    {"name": "State Govt", "slug": "state"},
    {"name": "Banking", "slug": "banking"},
    {"name": "Teaching", "slug": "teaching"},
    {"name": "Defence", "slug": "defence"},
    {"name": "Engineering", "slug": "engineering"},
    {"name": "Medical", "slug": "medical"},
    {"name": "Management", "slug": "management"},
    {"name": "Law", "slug": "law"},
    {"name": "PSU", "slug": "psu"},
    {"name": "Other", "slug": "other"},
]

for cat_info in categories_data:
    Category.objects.get_or_create(slug=cat_info["slug"], defaults=cat_info)

# ── EXAMS ──────────────────────────────────────

today = date.today()

exams_data = [
    {
        "name": "SSC CGL 2024",
        "category_slug": "central",
        "conducting_body": "Staff Selection Commission",
        "eligibility": "Bachelor's degree. Age: 18-32 years.",
        "syllabus": "Tier I: General Intelligence, English, Quant, GA",
        "vacancies": "17727",
        "official_link": "https://ssc.gov.in",
        "apply_link": "https://ssc.gov.in/login",
        "application_start_date": today - timedelta(days=10),
        "application_end_date": today + timedelta(days=20),
        "dates": [
            {"date_type": "exam", "date": today + timedelta(days=60)},
        ]
    },
    {
        "name": "IBPS PO XIV",
        "category_slug": "banking",
        "conducting_body": "IBPS",
        "eligibility": "Graduate. Age: 20-30 years.",
        "syllabus": "Prelims: English, Quant, Reasoning",
        "vacancies": "4455",
        "official_link": "https://ibps.in",
        "apply_link": "https://ibps.in/apply",
        "application_start_date": today - timedelta(days=30),
        "application_end_date": today - timedelta(days=5),
        "dates": [
            {"date_type": "exam", "date": today + timedelta(days=15)},
        ]
    },
    {
        "name": "NDA & NA (I) 2025",
        "category_slug": "defence",
        "conducting_body": "UPSC",
        "eligibility": "12th Pass. Unmarried males. Age: 16.5-19.5.",
        "syllabus": "Maths, GAT, SSB Interview",
        "vacancies": "400",
        "official_link": "https://upsc.gov.in",
        "apply_link": "https://upsc.gov.in/apply",
        "application_start_date": today + timedelta(days=5),
        "application_end_date": today + timedelta(days=35),
        "dates": [
            {"date_type": "exam", "date": today + timedelta(days=90)},
        ]
    },
    {
        "name": "JEE Main 2025 Session 2",
        "category_slug": "engineering",
        "conducting_body": "NTA",
        "eligibility": "12th Pass (PCM).",
        "syllabus": "Physics, Chemistry, Maths",
        "vacancies": None,
        "official_link": "https://jeemain.nta.nic.in",
        "apply_link": "https://jeemain.nta.nic.in/registration",
        "application_start_date": today - timedelta(days=5),
        "application_end_date": today + timedelta(days=10),
        "dates": [
            {"date_type": "exam", "date": today + timedelta(days=40)},
        ]
    },
    {
        "name": "NEET UG 2025",
        "category_slug": "medical",
        "conducting_body": "NTA",
        "eligibility": "12th Pass (PCB). Age: 17+.",
        "syllabus": "Bio, Physics, Chem",
        "vacancies": 100000,
        "official_link": "https://neet.nta.nic.in",
        "apply_link": "https://neet.nta.nic.in/apply",
        "application_start_date": today - timedelta(days=45),
        "application_end_date": today - timedelta(days=15),
        "dates": [
            {"date_type": "exam", "date": today + timedelta(days=50)},
        ]
    }
]

for exam_info in exams_data:
    dates = exam_info.pop("dates", [])
    cat_slug = exam_info.pop("category_slug")
    category = Category.objects.get(slug=cat_slug)
    exam, created = Exam.objects.get_or_create(
        name=exam_info["name"], 
        category=category,
        defaults=exam_info
    )
    if created:
        for d in dates:
            ExamDate.objects.create(exam=exam, **d)
        print(f"  [OK] Created exam: {exam.name}")
    else:
        # Update existing for testing
        for key, value in exam_info.items():
            setattr(exam, key, value)
        exam.save()
        print(f"  [UPDATED] Updated exam: {exam.name}")

# ── RESOURCES ──────────────────────────────────

resources_data = [
    {"title": "UPSC Prelims Previous Year Papers (2015-2026)", "resource_type": "PDF", "url": "https://upsc.gov.in/examinations/previous-question-papers"},
    {"title": "Indian Polity by M. Laxmikanth - Summary Notes", "resource_type": "PDF", "url": "https://example.com/polity-notes"},
    {"title": "Ancient Indian History - Complete Video Course", "resource_type": "VIDEO", "url": "https://youtube.com/playlist?list=example1"},
    {"title": "SSC CGL Quantitative Aptitude Practice Sets", "resource_type": "PDF", "url": "https://example.com/ssc-quant"},
    {"title": "Banking Awareness for IBPS PO 2027", "resource_type": "ARTICLE", "url": "https://example.com/banking-awareness"},
    {"title": "NEET Biology Chapter-wise Notes (NCERT Based)", "resource_type": "PDF", "url": "https://example.com/neet-bio-notes"},
    {"title": "JEE Main Physics - Mechanics Full Video Series", "resource_type": "VIDEO", "url": "https://youtube.com/playlist?list=example2"},
    {"title": "Current Affairs Monthly Digest - March 2027", "resource_type": "ARTICLE", "url": "https://example.com/current-affairs-march"},
    {"title": "NDA Maths Previous Year Solved Papers", "resource_type": "PDF", "url": "https://example.com/nda-maths"},
]

for res in resources_data:
    obj, created = Resource.objects.get_or_create(title=res["title"], defaults=res)
    if created:
        print(f"  [OK] Created resource: {obj.title}")
    else:
        print(f"  [SKIP] Skipped (exists): {obj.title}")

# ── QUIZ QUESTIONS ──────────────────────────────

questions_data = [
    {"subject": "HISTORY", "question_text": "Who founded the Maurya Dynasty?", "option_a": "Ashoka", "option_b": "Chandragupta Maurya", "option_c": "Bindusara", "option_d": "Bimbisara", "correct_answer": "B"},
    {"subject": "POLITY", "question_text": "How many fundamental rights are there in the Indian Constitution?", "option_a": "5", "option_b": "6", "option_c": "7", "option_d": "8", "correct_answer": "B"},
    {"subject": "GEOGRAPHY", "question_text": "Which is the longest river in India?", "option_a": "Yamuna", "option_b": "Godavari", "option_c": "Ganga", "option_d": "Brahmaputra", "correct_answer": "C"},
    {"subject": "ECONOMY", "question_text": "RBI was established in which year?", "option_a": "1935", "option_b": "1947", "option_c": "1950", "option_d": "1929", "correct_answer": "A"},
    {"subject": "SCIENCE", "question_text": "What is the chemical formula of table salt?", "option_a": "NaCl", "option_b": "KCl", "option_c": "CaCl2", "option_d": "NaOH", "correct_answer": "A"},
    {"subject": "CURRENT_AFFAIRS", "question_text": "Which country hosted the G20 summit in 2023?", "option_a": "Japan", "option_b": "India", "option_c": "Indonesia", "option_d": "Brazil", "correct_answer": "B"},
    {"subject": "HISTORY", "question_text": "The Battle of Plassey was fought in which year?", "option_a": "1757", "option_b": "1764", "option_c": "1857", "option_d": "1600", "correct_answer": "A"},
    {"subject": "POLITY", "question_text": "Who is known as the Father of the Indian Constitution?", "option_a": "Mahatma Gandhi", "option_b": "Jawaharlal Nehru", "option_c": "B.R. Ambedkar", "option_d": "Sardar Patel", "correct_answer": "C"},
    {"subject": "GEOGRAPHY", "question_text": "Which Indian state has the largest area?", "option_a": "Madhya Pradesh", "option_b": "Maharashtra", "option_c": "Uttar Pradesh", "option_d": "Rajasthan", "correct_answer": "D"},
    {"subject": "SCIENCE", "question_text": "Vitamin C is also known as?", "option_a": "Retinol", "option_b": "Ascorbic Acid", "option_c": "Thiamine", "option_d": "Tocopherol", "correct_answer": "B"},
]

for q in questions_data:
    obj, created = Question.objects.get_or_create(question_text=q["question_text"], defaults=q)
    if created:
        print(f"  [OK] Created question: {obj.question_text[:50]}...")
    else:
        print(f"  [SKIP] Skipped (exists): {obj.question_text[:50]}...")

# ── NEWS ALERTS ──────────────────────────────────

news_data = [
    {"title": "SSC CGL 2027 Notification Released!", "description": "SSC has officially released the CGL 2027 notification. Last date to apply: April 15, 2027.", "is_active": True},
    {"title": "NEET 2027 Registration Open", "description": "NTA has opened the NEET UG 2027 registration portal. Apply before March 20, 2027.", "is_active": True},
    {"title": "IBPS PO Prelims Result Declared", "description": "IBPS has declared the PO Prelims 2026 result. Check your scorecard on ibps.in.", "is_active": True},
]

for n in news_data:
    obj, created = NewsAlert.objects.get_or_create(title=n["title"], defaults=n)
    if created:
        print(f"  [OK] Created news: {obj.title}")
    else:
        print(f"  [SKIP] Skipped (exists): {obj.title}")

print("\nDONE: Database seeding complete!")
