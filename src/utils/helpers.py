"""Utility helper functions."""

import base64
import json
import time
from typing import Any, Dict
from pathlib import Path


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, timeout_seconds: int = 180):
        """
        Initialize timer.
        
        Args:
            timeout_seconds: Maximum allowed time in seconds
        """
        self.timeout_seconds = timeout_seconds
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        """Start the timer."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        """Stop the timer."""
        self.end_time = time.time()
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        current = self.end_time if self.end_time else time.time()
        return current - self.start_time
    
    def is_timeout(self) -> bool:
        """Check if timeout has been exceeded."""
        return self.elapsed() >= self.timeout_seconds
    
    def remaining(self) -> float:
        """Get remaining time in seconds."""
        return max(0.0, self.timeout_seconds - self.elapsed())


def validate_json(data: str) -> bool:
    """
    Validate if a string is valid JSON.
    
    Args:
        data: String to validate
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(data)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def get_payload_size(data: Dict[str, Any]) -> int:
    """
    Get the size of a JSON payload in bytes.
    
    Args:
        data: Dictionary to measure
        
    Returns:
        Size in bytes
    """
    return len(json.dumps(data).encode('utf-8'))


def encode_file_to_base64(file_path: str) -> str:
    """
    Encode a file to base64 string.
    
    Args:
        file_path: Path to file
        
    Returns:
        Base64 encoded string
    """
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def decode_base64_to_file(base64_str: str, output_path: str) -> None:
    """
    Decode base64 string and save to file.
    
    Args:
        base64_str: Base64 encoded string
        output_path: Path to save decoded file
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(base64.b64decode(base64_str))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
