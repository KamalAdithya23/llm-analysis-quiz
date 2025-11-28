# API Documentation

## Base URL

```
http://localhost:8000  (local development)
https://your-domain.com  (production)
```

## Endpoints

### POST /quiz

Receive a quiz task and start solving it.

**Request**

```http
POST /quiz HTTP/1.1
Content-Type: application/json

{
  "email": "student@example.com",
  "secret": "your-secret-string",
  "url": "https://example.com/quiz-123"
}
```

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string (email) | Yes | Student email address |
| secret | string | Yes | Secret string for verification |
| url | string (URL) | Yes | Quiz URL to solve |

**Response (200 OK)**

```json
{
  "status": "success",
  "message": "Quiz task received and processing started"
}
```

**Response (400 Bad Request)**

Invalid JSON payload:

```json
{
  "detail": "Invalid JSON payload"
}
```

Missing or invalid fields:

```json
{
  "detail": "Invalid request: field required"
}
```

**Response (403 Forbidden)**

Invalid secret:

```json
{
  "detail": "Invalid secret"
}
```

Invalid email:

```json
{
  "detail": "Invalid email"
}
```

**Example cURL**

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "secret": "my-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

---

### GET /health

Health check endpoint.

**Request**

```http
GET /health HTTP/1.1
```

**Response (200 OK)**

```json
{
  "status": "healthy"
}
```

**Example cURL**

```bash
curl http://localhost:8000/health
```

---

### GET /

Root endpoint with API information.

**Request**

```http
GET / HTTP/1.1
```

**Response (200 OK)**

```json
{
  "name": "LLM Analysis Quiz API",
  "version": "1.0.0",
  "endpoints": {
    "POST /quiz": "Submit a quiz task",
    "GET /health": "Health check",
    "GET /": "This endpoint"
  }
}
```

**Example cURL**

```bash
curl http://localhost:8000/
```

---

## Quiz Submission Flow

The application automatically submits answers to the quiz evaluation endpoint. This is not a direct API endpoint but shows the expected interaction.

### Submit Answer (External Endpoint)

**Request**

```http
POST https://example.com/submit HTTP/1.1
Content-Type: application/json

{
  "email": "student@example.com",
  "secret": "your-secret-string",
  "url": "https://example.com/quiz-123",
  "answer": 12345
}
```

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string (email) | Yes | Student email address |
| secret | string | Yes | Secret string for verification |
| url | string (URL) | Yes | Quiz URL being answered |
| answer | any | Yes | Answer (bool, int, str, dict, base64, etc.) |

**Response (200 OK) - Correct Answer**

```json
{
  "correct": true,
  "url": "https://example.com/quiz-456",
  "reason": null
}
```

**Response (200 OK) - Incorrect Answer**

```json
{
  "correct": false,
  "url": "https://example.com/quiz-456",
  "reason": "The sum you provided is incorrect."
}
```

**Response (200 OK) - Quiz Complete**

```json
{
  "correct": true,
  "url": null,
  "reason": null
}
```

---

## Error Codes

| Code | Description | Cause |
|------|-------------|-------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid JSON or missing required fields |
| 403 | Forbidden | Invalid email or secret |
| 500 | Internal Server Error | Unhandled server error |

---

## Answer Types

The `answer` field in the submission can be various types:

### Boolean

```json
{
  "answer": true
}
```

### Number (Integer)

```json
{
  "answer": 12345
}
```

### Number (Float)

```json
{
  "answer": 123.45
}
```

### String

```json
{
  "answer": "New York"
}
```

### Base64 File (Image/Chart)

```json
{
  "answer": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

### JSON Object

```json
{
  "answer": {
    "total": 12345,
    "average": 123.45,
    "count": 100
  }
}
```

---

## Rate Limits

No explicit rate limits are enforced, but:

- Each quiz must be solved within **3 minutes** of receiving the POST request
- Payload size is limited to **1MB**
- Only one quiz chain is processed at a time per instance

---

## Testing

### Demo Endpoint

Test your implementation with the demo endpoint:

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

### Invalid JSON Test

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d 'invalid json'
```

Expected: 400 Bad Request

### Invalid Secret Test

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "wrong-secret",
    "url": "https://example.com/quiz"
  }'
```

Expected: 403 Forbidden

---

## Authentication

Authentication is done via the `email` and `secret` fields in the request body. Both must match the values configured in your `.env` file.

**Security Notes**:
- Always use HTTPS in production
- Keep your secret confidential
- Rotate secrets periodically
- Never commit `.env` to version control

---

## Monitoring

### Logs

Logs are written to:
- Console (stdout)
- File: `logs/app.log`

Log format:
```
2025-11-28 20:30:00 - llm_quiz - INFO - Quiz task received for URL: https://example.com/quiz-123
```

### Health Monitoring

Use the `/health` endpoint for uptime monitoring:

```bash
# Check every 60 seconds
watch -n 60 'curl -s http://localhost:8000/health | jq'
```

---

## OpenAPI Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Request/response schemas
- Example payloads
- Authentication testing
