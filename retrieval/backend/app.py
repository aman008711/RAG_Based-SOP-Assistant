from fastapi import FastAPI

app = FastAPI(
    title="Document QA Backend API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Backend is running"}

@app.get("/health")
def health():
    return {"status": "OK"}


from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time

app = FastAPI(title="Streaming Chat API")

def chat_generator(question: str):
    """
    Simulates AI token-by-token generation
    """
    answer = (
        f"You asked: {question}. "
        "This response is streamed word by word using FastAPI StreamingResponse. "
        "This creates a ChatGPT like typewriter effect."
    )

    for word in answer.split():
        yield word + " "
        time.sleep(0.25)  # simulate token delay

@app.get("/chat")
def chat(question: str):
    return StreamingResponse(
        chat_generator(question),
        media_type="text/plain"
    )