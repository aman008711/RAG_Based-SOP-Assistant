from fastapi import FastAPI
from pydantic import BaseModel
from retrieval.retrieve import retrieve_answer


app = FastAPI()

class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: QueryRequest):
    return retrieve_answer(req.question)

