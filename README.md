# Protokal 2.0 - AI Chat Application

אפליקציית צ'אט מבוססת AI המתמחה בפרוטוקולים של ועד מקומי ריחן.

## תכונות

- 🤖 AI Chat עם OpenAI GPT-4
- 🔍 RAG (Retrieval-Augmented Generation) עם Google Vertex AI
- 🌐 REST API עם FastAPI
- 🐳 מוכן לפריסה ב-Cloud Run
- 🔒 תמיכה ב-CORS
- 📊 Health checks

## התקנה מקומית

### דרישות מקדימות

- Python 3.11+
- OpenAI API Key
- Google Cloud Project עם Vertex AI מופעל

### התקנה

1. שכפל את הפרויקט:
```bash
git clone <repository-url>
cd protokal_2.0
```

2. צור virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. התקן תלויות:
```bash
pip install -r requirements.txt
```

4. צור קובץ `.env` עם המשתנים הנדרשים (ראה `ENVIRONMENT.md`)

5. הרץ את האפליקציה:
```bash
python main.py
```

האפליקציה תהיה זמינה ב-`http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health status
- `POST /chat` - Send message to AI
- `POST /clear` - Clear chat history

### דוגמה לשימוש ב-API

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "מה הוחלט בפרוטוקול האחרון?"}'
```

## פריסה ל-Cloud Run

ראה `DEPLOYMENT.md` להוראות מפורטות.

## מבנה הפרויקט

```
protokal_2.0/
├── main.py              # קובץ האפליקציה הראשי
├── requirements.txt     # תלויות Python
├── Dockerfile          # הגדרת Docker
├── .dockerignore       # קבצים להתעלמות ב-Docker
├── .gcloudignore       # קבצים להתעלמות ב-Cloud Run
├── .gitignore          # קבצים להתעלמות ב-Git
├── DEPLOYMENT.md       # הוראות פריסה
├── ENVIRONMENT.md      # הגדרת משתני סביבה
├── SA.json            # Service Account (לא ב-Git)
└── README.md          # קובץ זה
```

## רישיון

MIT License