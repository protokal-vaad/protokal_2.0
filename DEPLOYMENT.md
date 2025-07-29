# פריסה ל-Cloud Run

## דרישות מקדימות

1. התקן את Google Cloud CLI
2. התחבר לחשבון Google Cloud שלך:
   ```bash
   gcloud auth login
   ```
3. הגדר את הפרויקט:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

## הוראות פריסה

### 1. בניית Image והעלאה ל-Container Registry

```bash
# בניית ה-image
docker build -t gcr.io/YOUR_PROJECT_ID/protokal-app .

# העלאה ל-Container Registry
docker push gcr.io/YOUR_PROJECT_ID/protokal-app
```

### 2. פריסה ל-Cloud Run

```bash
gcloud run deploy protokal-app \
  --image gcr.io/YOUR_PROJECT_ID/protokal-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 80 \
  --max-instances 10
```

### 3. הגדרת משתני סביבה

אם אתה צריך להגדיר משתני סביבה (כמו OPENAI_API_KEY), השתמש בפקודה:

```bash
gcloud run services update protokal-app \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=your_api_key_here
```

## בדיקת הפריסה

לאחר הפריסה, תוכל לבדוק את האפליקציה:

```bash
# קבלת ה-URL של השירות
gcloud run services describe protokal-app --region us-central1 --format="value(status.url)"

# בדיקת הלוגים
gcloud logs read --service=protokal-app --limit=50
```

## נקודות חשובות

1. **אבטחה**: קובץ `SA.json` מכיל פרטי אימות ל-Google Cloud. וודא שהוא מוגדר כ-Secret ב-Cloud Run.

2. **משאבים**: האפליקציה מוגדרת עם 2GB RAM ו-2 CPU cores. התאם לפי הצורך.

3. **Timeout**: מוגדר ל-5 דקות (300 שניות). התאם לפי הצורך.

4. **Concurrency**: מוגדר ל-80 בקשות במקביל. התאם לפי הצורך.

## הגדרת Secrets (מומלץ)

במקום לכלול את `SA.json` ב-image, מומלץ להשתמש ב-Cloud Secret Manager:

```bash
# יצירת secret
echo -n "$(cat SA.json)" | gcloud secrets create protokal-sa --data-file=-

# עדכון השירות להשתמש ב-secret
gcloud run services update protokal-app \
  --region us-central1 \
  --set-secrets GOOGLE_APPLICATION_CREDENTIALS=/secrets/protokal-sa:protokal-sa:latest
```

ואז עדכן את הקוד ב-`main.py`:

```python
# במקום:
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "SA.json"

# השתמש ב:
import json
from google.cloud import secretmanager

def get_sa_credentials():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/YOUR_PROJECT_ID/secrets/protokal-sa/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return json.loads(response.payload.data.decode("UTF-8"))

# הגדרת credentials
credentials = get_sa_credentials()
``` 