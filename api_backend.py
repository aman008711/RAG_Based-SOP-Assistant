from fastapi import FastAPI, Request
from pydantic import BaseModel
from retrieval.retrieve import retrieve_answer
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: {"detail": "Rate limit exceeded"})

class QueryRequest(BaseModel):
    question: str


@app.get("/health")
@limiter.limit("30/minute")
def health(request: Request):
    """Health check endpoint - Limited to 30 requests per minute"""
    return {"status": "ok"}

@app.post("/ask")
@limiter.limit("10/minute")
def ask(request: Request, req: QueryRequest):
    """Ask endpoint - Limited to 10 requests per minute"""
    return retrieve_answer(req.question)

