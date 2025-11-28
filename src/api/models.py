"""Pydantic models for API request/response validation."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Any


class QuizRequest(BaseModel):
    """Request model for quiz endpoint."""
    
    email: EmailStr = Field(..., description="Student email address")
    secret: str = Field(..., description="Secret string for verification")
    url: str = Field(..., description="Quiz URL to solve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "secret": "my-secret-string",
                "url": "https://example.com/quiz-123"
            }
        }


class QuizResponse(BaseModel):
    """Response model for quiz endpoint."""
    
    status: str = Field(..., description="Status of the request")
    message: str = Field(..., description="Human-readable message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Quiz task received and processing started"
            }
        }


class SubmitRequest(BaseModel):
    """Request model for submitting quiz answers."""
    
    email: EmailStr = Field(..., description="Student email address")
    secret: str = Field(..., description="Secret string for verification")
    url: str = Field(..., description="Quiz URL being answered")
    answer: Any = Field(..., description="Answer to the quiz (can be bool, int, str, dict, etc.)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "secret": "my-secret-string",
                "url": "https://example.com/quiz-123",
                "answer": 12345
            }
        }


class SubmitResponse(BaseModel):
    """Response model from quiz submission endpoint."""
    
    correct: bool = Field(..., description="Whether the answer was correct")
    url: Optional[str] = Field(None, description="Next quiz URL if available")
    reason: Optional[str] = Field(None, description="Reason for incorrect answer")
    
    class Config:
        json_schema_extra = {
            "example": {
                "correct": True,
                "url": "https://example.com/quiz-456",
                "reason": None
            }
        }
