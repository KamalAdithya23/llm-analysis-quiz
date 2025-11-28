"""FastAPI server for receiving and processing quiz tasks."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import asyncio
from typing import Dict, Any

from src.api.models import QuizRequest, QuizResponse
from src.config import settings
from src.utils.logger import logger
from src.solver.quiz_solver import QuizSolver


app = FastAPI(
    title="LLM Analysis Quiz API",
    description="API endpoint for receiving and solving quiz tasks",
    version="1.0.0"
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.post("/quiz", response_model=QuizResponse, status_code=200)
async def receive_quiz(request: Request):
    """
    Receive a quiz task and start solving it.
    
    Args:
        request: FastAPI request object
        
    Returns:
        QuizResponse indicating task received
        
    Raises:
        HTTPException: 400 for invalid JSON, 403 for invalid secret
    """
    # Parse JSON
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON received: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Validate request
    try:
        quiz_request = QuizRequest(**body)
    except Exception as e:
        logger.error(f"Request validation failed: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    
    # Verify secret
    if quiz_request.secret != settings.secret:
        logger.warning(f"Invalid secret received from {quiz_request.email}")
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Verify email
    if quiz_request.email != settings.email:
        logger.warning(f"Invalid email received: {quiz_request.email}")
        raise HTTPException(status_code=403, detail="Invalid email")
    
    logger.info(f"Quiz task received for URL: {quiz_request.url}")
    
    # Start quiz solving in background
    asyncio.create_task(solve_quiz_task(quiz_request))
    
    return QuizResponse(
        status="success",
        message="Quiz task received and processing started"
    )


async def solve_quiz_task(quiz_request: QuizRequest):
    """
    Solve a quiz task in the background.
    
    Args:
        quiz_request: Validated quiz request
    """
    try:
        solver = QuizSolver()
        await solver.solve_quiz_chain(
            initial_url=quiz_request.url,
            email=quiz_request.email,
            secret=quiz_request.secret
        )
        logger.info(f"Quiz chain completed for {quiz_request.url}")
    except Exception as e:
        logger.error(f"Error solving quiz: {e}", exc_info=True)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LLM Analysis Quiz API",
        "version": "1.0.0",
        "endpoints": {
            "POST /quiz": "Submit a quiz task",
            "GET /health": "Health check",
            "GET /": "This endpoint"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
