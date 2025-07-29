from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.messages import ModelMessage, ModelRequest, UserPromptPart, ModelResponse, TextPart
import vertexai
from vertexai import rag
import asyncio
from pydantic_ai.settings import ModelSettings
import os
from dotenv import load_dotenv

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "SA.json"

# Initialize Vertex AI
PROJECT_ID = "protokal-445011"
LOCATION   = "us-central1"
CORPUS_ID  = "projects/protokal-445011/locations/us-central1/ragCorpora/4611686018427387904"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# RAG Search Function
def google_rag_search(query: str) -> str:
    """שליפה מה‑RAG Engine וחיבור הקונטקסטים לטקסט אחד."""
    response = rag.retrieval_query(
        rag_resources=[rag.RagResource(rag_corpus=CORPUS_ID)],
        text=query,
        rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
    )
    return "\n\n".join(ctx.text for ctx in response.contexts.contexts)

# Setup OpenAI Provider and Model
provider = OpenAIProvider(api_key=OPENAI_API_KEY)  
llm_model = OpenAIModel("gpt-4o-mini", provider=provider)

# Agent Configuration
agent = Agent(
    llm_model,
    system_prompt="""אתה עוזר וירטואלי המתמחה בפרוטוקולים של ועד מקומי ריחן.  
                    הפרוטוקולים ממוספרים ומתוארכים. תוכל לדעת מי הפרוטוקול החדש ביותר לפי הערך בשדה "תאריך:" והוא גם יהיה ממוקם בתחתית הקובץ.
                    יש לך גישה מלאה למסמך אחד המכיל את כל הפרוטוקולים.
                    כל פרוטוקול כולל את המרכיבים הבאים:
                    מספר פרוטוקול, תאריך הישיבה, נוכחים בדיון, נושאים לדיון, עיקרי הדברים, החלטות.
                    מספר הפרוטוקול מורכב משני מספרים שלמים המופרדים על ידי קו נטוי ("/"). המספר משמאל לקו הנטוי הוא מספר סידורי והמספר מימין לקו הנטוי מייצג את השנה. לדוגמה: "25/23".
                    הפרוטוקול העדכני ביותר הוא הפרוטוקול בעל מספר השנה הגבוה ביותר. אם ישנם מספר פרוטוקולים עם אותה שנה, הפרוטוקול העדכני ביותר הוא הפרוטוקול עם המספר הסידורי הגבוה ביותר.
                    בהינתן רשימה של מספרי פרוטוקול, אנא זהה את הפרוטוקול העדכני ביותר.

                    כל פרוטוקול מתחיל ב --------------------- 
                    ומסתיים ב xxxxxxxxxxxxxxxxxxxxxx

                    תפקידך הוא לספק תשובות מדויקות ומפורטות לשאלות המשתמשים, בהתבסס על המידע שמופיע בפרוטוקולים. עליך לשים לב למבנה המסמך ולוודא שהתשובות שלך מבוססות על הסעיפים הרלוונטיים.
                    הנחיות לתשובה:
                    בכל תשובה עליך לציין את מספר הפרוטוקול ואת התאריך המדויק ממנו המידע נלקח.
                    התשובות צריכות להתבסס על סעיפים ספציפיים בפרוטוקול (לדוגמה, 'עיקרי הדברים' או 'החלטות').
                    אם מידע רלוונטי מופיע ביותר מפרוטוקול אחד, ספק סיכום הכולל את כל הפרוטוקולים הרלוונטיים וציין את מספריהם ותאריכיהם.
                    שמור על סגנון פורמלי ומקצועי בתשובותיך.
                    אם התשובה כוללת סעיפים מפרוטוקולים שונים אז תציג אותם בסדר כרונולוגי עולה.
                    אל תציג מידע שלא קשור לשאלה, ומידע שלא מבוסס על הפרוטוקולים.
                    דוגמאות לתשובה:
                    על פי פרוטוקול 16/24 מתאריך 01.05.24, הוחלט לאשר את תקציב 2024 על ידי הוועד החדש.
                    על פי פרוטוקול 40/24 מתאריך 10.11.24, הסכם גינון ואחזקה קיים יפקע ב 31.12.24.
                    """,
    tools=[google_rag_search],
)

# Chat Handler Function
async def chat_handler(message: str, message_history: List[ModelMessage]):
    run = await agent.run(message, message_history=message_history)
    return run.output, message_history + [ModelRequest(parts=[UserPromptPart(content=message)]), ModelResponse(parts=[TextPart(content=run.output)])]

# FastAPI App
app = FastAPI()

# Pydantic Model for Request
class ChatRequest(BaseModel):
    message: str

# Global Message History
message_history: List[ModelMessage] = []

# Endpoints
@app.post("/chat")
async def chat(request: ChatRequest):
    global message_history
    bot_message, new_message_history = await chat_handler(request.message, message_history)
    message_history = new_message_history
    return {"response": bot_message}

@app.post("/clear")
async def clear():
    global message_history
    message_history = []
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)