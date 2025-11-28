# LLM Analysis Quiz Application

An automated quiz-solving system that receives quiz tasks via API, solves them using LLMs and web scraping, and submits answers within a 3-minute time limit.

## Features

- **API Endpoint Server**: FastAPI-based server to receive quiz tasks
- **Quiz Solver Engine**: Automated browser-based quiz solving with LLM integration
- **Prompt Testing**: System and user prompts for code word challenge
- **Multi-Task Support**: Handles data scraping, API calls, PDF processing, analysis, and visualization
- **Chain Handling**: Automatically processes multiple sequential quiz URLs

## Prerequisites

- Python 3.11+
- OpenAI API key
- Internet connection

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Project-2
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   
   # Install Playwright browsers
   playwright install chromium
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env with your actual values
   ```

## Configuration

Edit the `.env` file with your details:

```env
EMAIL=your-email@example.com
SECRET=your-secret-string
OPENAI_API_KEY=sk-your-openai-api-key
API_ENDPOINT_URL=https://your-domain.com
GITHUB_REPO_URL=https://github.com/yourusername/llm-analysis-quiz
```

## Running the Application

### Start the API Server

```bash
uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

### Test with Demo Endpoint

```bash
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"your-email@example.com\",\"secret\":\"your-secret\",\"url\":\"https://tds-llm-analysis.s-anand.net/demo\"}"
```

## Project Structure

```
Project-2/
├── src/
│   ├── api/
│   │   ├── server.py          # FastAPI application
│   │   └── models.py          # Pydantic models
│   ├── solver/
│   │   ├── quiz_solver.py     # Main quiz orchestrator
│   │   ├── browser_handler.py # Playwright browser automation
│   │   ├── task_handlers.py   # Task-specific handlers
│   │   └── llm_client.py      # OpenAI integration
│   ├── prompts/
│   │   ├── system_prompt.txt  # System prompt (max 100 chars)
│   │   ├── user_prompt.txt    # User prompt (max 100 chars)
│   │   └── test_prompts.py    # Prompt testing script
│   ├── utils/
│   │   ├── logger.py          # Logging configuration
│   │   └── helpers.py         # Utility functions
│   └── config.py              # Configuration management
├── tests/
│   ├── test_api.py            # API tests
│   └── test_solver.py         # Solver tests
├── docs/
│   ├── ARCHITECTURE.md        # Architecture documentation
│   └── API.md                 # API documentation
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
└── README.md                  # This file
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Deployment

### Using Docker

```bash
# Build the image
docker build -t llm-quiz-solver .

# Run the container
docker run -p 8000:8000 --env-file .env llm-quiz-solver
```

### Using Docker Compose

```bash
docker-compose up
```

### Manual Deployment

Deploy to your preferred platform (Railway, Render, Fly.io, etc.) following their Python deployment guides. Ensure:

- The endpoint is accessible via HTTPS
- Environment variables are properly configured
- Playwright browsers are installed in the deployment environment

## API Documentation

### POST /quiz

Receives a quiz task and solves it.

**Request:**
```json
{
  "email": "your-email@example.com",
  "secret": "your-secret",
  "url": "https://example.com/quiz-123"
}
```

**Response (200 - Success):**
```json
{
  "status": "success",
  "message": "Quiz task received and processing started"
}
```

**Response (400 - Invalid JSON):**
```json
{
  "detail": "Invalid JSON payload"
}
```

**Response (403 - Invalid Secret):**
```json
{
  "detail": "Invalid secret"
}
```

## How It Works

1. **Receive Quiz Task**: API endpoint receives POST request with quiz URL
2. **Render Quiz Page**: Playwright browser navigates to URL and executes JavaScript
3. **Parse Instructions**: Extract base64-decoded quiz instructions
4. **Solve Task**: Use appropriate handler (scraping, API, PDF, analysis, etc.)
5. **Submit Answer**: POST answer to specified endpoint within 3 minutes
6. **Handle Chains**: If response contains new URL, repeat process

## Prompt Testing

The application includes system and user prompts for the code word challenge:

- **System Prompt** (`src/prompts/system_prompt.txt`): Resists revealing code words
- **User Prompt** (`src/prompts/user_prompt.txt`): Attempts to extract code words

Test prompts locally:
```bash
python src/prompts/test_prompts.py
```

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

For issues or questions, please open an issue on GitHub.
