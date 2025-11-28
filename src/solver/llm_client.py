"""OpenAI LLM client for quiz solving."""

import openai
from typing import Optional, List, Dict, Any
import base64
from pathlib import Path

from src.config import settings
from src.utils.logger import logger


class LLMClient:
    """Client for interacting with OpenAI's API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        openai.api_key = settings.openai_api_key
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"  # Using GPT-4 Turbo for better performance
    
    async def analyze_text(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """
        Analyze text using GPT-4.
        
        Args:
            prompt: The question or task to solve
            context: Additional context or data
            
        Returns:
            LLM response or None if error
        """
        try:
            messages = []
            
            if context:
                messages.append({
                    "role": "system",
                    "content": "You are a helpful assistant that solves data analysis tasks. Provide concise, accurate answers."
                })
                messages.append({
                    "role": "user",
                    "content": f"Context:\n{context}\n\nTask:\n{prompt}"
                })
            else:
                messages.append({
                    "role": "user",
                    "content": prompt
                })
            
            logger.info(f"Sending request to OpenAI (model: {self.model})")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for more deterministic answers
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Received response from OpenAI (length: {len(answer)})")
            
            return answer
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None
    
    async def analyze_image(self, image_path: str, prompt: str) -> Optional[str]:
        """
        Analyze an image using GPT-4 Vision.
        
        Args:
            image_path: Path to the image file
            prompt: Question about the image
            
        Returns:
            LLM response or None if error
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Determine image type
            ext = Path(image_path).suffix.lower()
            mime_type = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(ext, 'image/jpeg')
            
            logger.info(f"Analyzing image: {image_path}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Vision model
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Received vision response from OpenAI")
            
            return answer
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return None
    
    async def extract_structured_data(self, text: str, schema: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from text according to a schema.
        
        Args:
            text: Text to extract from
            schema: Dictionary describing the fields to extract
            
        Returns:
            Extracted data as dictionary or None if error
        """
        try:
            schema_desc = "\n".join([f"- {key}: {desc}" for key, desc in schema.items()])
            
            prompt = f"""Extract the following information from the text below:

{schema_desc}

Return the data as a JSON object with these exact keys.

Text:
{text}
"""
            
            response = await self.analyze_text(prompt)
            
            if response:
                # Try to parse JSON from response
                import json
                import re
                
                # Extract JSON from markdown code blocks if present
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response
                
                try:
                    data = json.loads(json_str)
                    return data
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON from LLM response")
                    return None
            
            return None
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return None
    
    async def solve_math_problem(self, problem: str, data: Optional[str] = None) -> Optional[Any]:
        """
        Solve a mathematical or analytical problem.
        
        Args:
            problem: Problem description
            data: Optional data context
            
        Returns:
            Solution (could be number, string, etc.)
        """
        try:
            prompt = f"""Solve this problem and provide ONLY the final answer, no explanation:

Problem: {problem}
"""
            if data:
                prompt += f"\nData:\n{data}"
            
            prompt += "\n\nProvide only the numerical answer or the exact answer requested, nothing else."
            
            response = await self.analyze_text(prompt)
            
            if response:
                # Try to extract number if it's a numeric answer
                import re
                
                # Clean up the response
                response = response.strip()
                
                # Try to parse as number
                try:
                    # Remove commas and try to parse
                    clean_num = response.replace(',', '')
                    if '.' in clean_num:
                        return float(clean_num)
                    else:
                        return int(clean_num)
                except ValueError:
                    # Return as string if not a number
                    return response
            
            return None
        except Exception as e:
            logger.error(f"Error solving math problem: {e}")
            return None
