"""
Simple test FastAPI server
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import asyncio
import time

app = FastAPI(title="Test API")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/ask")
async def ask_question(question: str = "test"):
    async def generate_response():
        yield "data: Starting response...\n\n"
        await asyncio.sleep(0.1)
        yield f"data: Question: {question}\n\n"
        await asyncio.sleep(0.1)
        yield "data: Answer: This is a test response\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/web")
async def web_interface():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Chat</title>
    </head>
    <body>
        <h1>Test Chat Interface</h1>
        <input type="text" id="question" placeholder="Ask a question...">
        <button onclick="askQuestion()">Ask</button>
        <div id="response"></div>

        <script>
        async function askQuestion() {
            const question = document.getElementById('question').value;
            const responseDiv = document.getElementById('response');
            responseDiv.innerHTML = 'Loading...';

            const response = await fetch(`/ask?question=${encodeURIComponent(question)}`);
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            responseDiv.innerHTML = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') break;
                        responseDiv.innerHTML += data + '<br>';
                    }
                }
            }
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)