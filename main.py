# main.py
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import openai

from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import re
import pyttsx3
from database import SessionLocal, create_tables
from models import Conversation
from sqlalchemy.orm import Session

load_dotenv()  
app = FastAPI()


create_tables()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular's default dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)
print(os.environ.get("OPENAI_API_KEY"))
# GPT API key

openai.api_key = os.environ.get("OPENAI_API_KEY")
openai.base_url = os.environ.get("BASE_URL")

# Data model for receiving user message
class Message(BaseModel):
    message: str

def clean_response(response_text: str) -> str:
    # Remove phrases enclosed in asterisks (*)
    cleaned_text = re.sub(r'\*.*?\*', '', response_text)
    
    # Remove any emojis using regex for Unicode ranges
    emoji_pattern = re.compile(
        "[" 
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA00-\U0001FA6F"  # Chess Symbols
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE
    )
    cleaned_text = emoji_pattern.sub(r'', cleaned_text)
    
    # Remove unnecessary extra spaces
    cleaned_text = ' '.join(cleaned_text.split())
    
    return cleaned_text

# Interact with GPT API to get AI response
async def generate_gpt_response(user_message: str) -> str:


    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[

        {"role": "system", "content": "You are a professional assistant. Respond clearly and concisely without including any meta-comments, explanations, or formatting notes. Only respond with the final answer.Respond with a short answer and keep it engaging"},
        {"role": "user", "content": user_message},
    ],
    )
    cleaned_response = clean_response(completion.choices[0].message.content)

    return cleaned_response


# API route for receiving user messages and returning GPT responses
@app.post("/api/message")
async def get_message(message: Message,db: Session = Depends(get_db)):
    user_message = message.message
    ai_response = await generate_gpt_response(user_message)

    conversation = Conversation(user=user_message, bot=ai_response)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {"response": ai_response}

# Retrieve conversations
@app.get("/api/conversations")
def get_conversations(db: Session = Depends(get_db)):
    return db.query(Conversation).all()