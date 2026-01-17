# API Rate Limiting Documentation

## Overview
Rate limiting has been implemented to prevent abuse and ensure fair usage of the RAG-Based SOP Assistant API.

## What's Included

### 1. **Package Addition**
- Added `slowapi` to `requirements.txt` - a production-ready rate limiting library for FastAPI

### 2. **Rate Limits Applied**

#### main.py endpoints:
| Endpoint | Method | Rate Limit | Purpose |
|----------|--------|-----------|---------|
| `/health` | GET | 30/minute | Health checks |
| `/ask` | GET | 10/minute | Query processing (streaming) |
| `/ask` | POST | 10/minute | Query processing (streaming) |
| `/` | GET | 30/minute | API documentation |
| `/web` | GET | 20/minute | Web interface access |

#### api_backend.py endpoints:
| Endpoint | Method | Rate Limit | Purpose |
|----------|--------|-----------|---------|
| `/health` | GET | 30/minute | Health checks |
| `/ask` | POST | 10/minute | Query processing |

## How It Works

### Rate Limiting Strategy
- **Per-IP Address**: Limits are based on the client's IP address
- **Time Window**: Requests are counted per minute (60-second window)
- **Response**: When limit exceeded, clients receive HTTP 429 (Too Many Requests) with error message

### Example Response When Rate Limited
```json
{
  "detail": "Rate limit exceeded"
}
```

## Implementation Details

### Key Components Added

1. **Limiter Initialization**
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   ```

2. **Exception Handler**
   ```python
   app.add_exception_handler(RateLimitExceeded, lambda request, exc: {"detail": "Rate limit exceeded"})
   ```

3. **Endpoint Decorators**
   ```python
   @app.post("/ask")
   @limiter.limit("10/minute")
   async def ask_question(request: Request, ...):
       ...
   ```

## Rate Limit Rationale

### Query Endpoints (10/minute)
- The `/ask` endpoints are resource-intensive (embedding + vector search + LLM)
- 10 requests/minute = 1 request every 6 seconds per client
- Sufficient for normal usage, prevents abuse

### Health Checks (30/minute)
- Light-weight operations, safe to allow more frequently
- 30 requests/minute = monitoring and health checks acceptable

### Root & Web Interface (20-30/minute)
- Meta-endpoints with minimal computational overhead
- Support reasonable monitoring and documentation access

## Testing Rate Limits

### Using curl (Linux/macOS/WSL):
```bash
# Make 15 rapid requests to trigger rate limit
for i in {1..15}; do curl -X GET "http://localhost:8008/health"; done
```

### Using curl (Windows PowerShell):
```powershell
# Make 15 rapid requests
1..15 | ForEach-Object { curl.exe -X GET "http://localhost:8008/health" }
```

### Expected Behavior:
- First 10 requests: `{"status": "healthy", ...}`
- Requests 11+: `{"detail": "Rate limit exceeded"}`

## Configuration

### To Modify Rate Limits
Edit the `@limiter.limit()` decorator in:
- `main.py` - FastAPI backend endpoints
- `api_backend.py` - Alternative backend endpoints

### Example: Increase query limit to 20/minute
```python
@app.post("/ask")
@limiter.limit("20/minute")  # Changed from 10/minute
async def ask_question(request: Request, ...):
    ...
```

### Other Rate Limit Formats
```python
@limiter.limit("5/second")      # Per second
@limiter.limit("100/hour")      # Per hour
@limiter.limit("1000/day")      # Per day
```

## Benefits

✅ **Prevents Abuse**: Stops DDoS attempts and malicious scraping
✅ **Fair Usage**: Ensures all users get reasonable API access
✅ **Resource Protection**: Prevents system overload
✅ **Cost Control**: Limits expensive LLM API calls
✅ **Monitoring**: Track unusual access patterns

## Future Enhancements

### Potential Improvements:
1. **API Keys**: Different rate limits for authenticated vs anonymous users
2. **Tiered Limits**: Premium users with higher limits
3. **Dynamic Limits**: Adjust based on system load
4. **Redis Backend**: Distributed rate limiting across multiple servers
5. **Cost-Based Limits**: Different limits for different operations

## Troubleshooting

### Issue: "Rate limit exceeded" too quickly?
**Solution**: Increase the limit values in the decorators

### Issue: Rate limiting not working?
**Ensure**:
1. `slowapi` is installed: `pip install slowapi`
2. `Request` parameter is included in function signature
3. Decorator is properly placed above the endpoint

### Issue: Need different limits per user?
**Solution**: Use API keys with the authenticated limiter:
```python
from slowapi.util import get_remote_address
# Or use custom key function
def get_api_key(request: Request):
    return request.headers.get("X-API-Key", get_remote_address(request))

limiter = Limiter(key_func=get_api_key)
```

## Installation

Ensure `slowapi` is installed:
```bash
pip install -r requirements.txt
# OR
pip install slowapi
```

## References

- **slowapi**: https://github.com/laurentS/slowapi
- **FastAPI Rate Limiting**: https://fastapi.tiangolo.com/advanced/middleware/#using-slowapi-for-rate-limiting
