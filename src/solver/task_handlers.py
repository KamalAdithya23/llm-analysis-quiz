"""Task handlers for different types of quiz questions."""

import re
import json
from typing import Any, Optional, Dict, List
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import httpx
from PyPDF2 import PdfReader

from src.utils.logger import logger
from src.solver.llm_client import LLMClient
from src.solver.browser_handler import BrowserHandler


class TaskHandler:
    """Base class for task handlers."""
    
    def __init__(self):
        """Initialize task handler."""
        self.llm_client = LLMClient()
    
    async def handle(self, task_description: str, context: Dict[str, Any]) -> Any:
        """
        Handle a task.
        
        Args:
            task_description: Description of the task
            context: Additional context (URLs, data, etc.)
            
        Returns:
            Answer to the task
        """
        raise NotImplementedError


class DataScrapingHandler(TaskHandler):
    """Handler for web scraping tasks."""
    
    async def handle(self, task_description: str, context: Dict[str, Any]) -> Any:
        """Scrape data from a website."""
        try:
            url = context.get('url')
            if not url:
                logger.error("No URL provided for scraping")
                return None
            
            async with BrowserHandler() as browser:
                await browser.navigate_to(url)
                content = await browser.get_page_content()
                
                # Use LLM to extract the required information
                answer = await self.llm_client.analyze_text(
                    prompt=task_description,
                    context=f"HTML Content:\n{content[:10000]}"  # Limit context size
                )
                
                return answer
        except Exception as e:
            logger.error(f"Error in data scraping: {e}")
            return None


class PDFProcessingHandler(TaskHandler):
    """Handler for PDF processing tasks."""
    
    async def handle(self, task_description: str, context: Dict[str, Any]) -> Any:
        """Process PDF files."""
        try:
            pdf_path = context.get('pdf_path')
            if not pdf_path:
                logger.error("No PDF path provided")
                return None
            
            # Read PDF
            reader = PdfReader(pdf_path)
            
            # Extract text from all pages or specific page
            page_num = context.get('page_number')
            if page_num:
                text = reader.pages[page_num - 1].extract_text()
            else:
                text = "\n".join([page.extract_text() for page in reader.pages])
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            
            # Use LLM to analyze the PDF content
            answer = await self.llm_client.analyze_text(
                prompt=task_description,
                context=f"PDF Content:\n{text}"
            )
            
            return answer
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return None


class DataAnalysisHandler(TaskHandler):
    """Handler for data analysis tasks."""
    
    async def handle(self, task_description: str, context: Dict[str, Any]) -> Any:
        """Analyze data (CSV, JSON, tables, etc.)."""
        try:
            data = context.get('data')
            data_type = context.get('data_type', 'text')
            
            if data_type == 'csv':
                # Parse CSV data
                df = pd.read_csv(data) if isinstance(data, str) and Path(data).exists() else pd.read_csv(pd.io.common.StringIO(data))
                data_str = df.to_string()
            elif data_type == 'json':
                # Parse JSON data
                data_obj = json.loads(data) if isinstance(data, str) else data
                data_str = json.dumps(data_obj, indent=2)
            else:
                data_str = str(data)
            
            # Use LLM to analyze
            answer = await self.llm_client.solve_math_problem(
                problem=task_description,
                data=data_str
            )
            
            return answer
        except Exception as e:
            logger.error(f"Error in data analysis: {e}")
            return None


class APIHandler(TaskHandler):
    """Handler for API-based tasks."""
    
    async def handle(self, task_description: str, context: Dict[str, Any]) -> Any:
        """Make API calls and process responses."""
        try:
            url = context.get('url')
            headers = context.get('headers', {})
            method = context.get('method', 'GET')
            
            async with httpx.AsyncClient() as client:
                if method.upper() == 'GET':
                    response = await client.get(url, headers=headers)
                elif method.upper() == 'POST':
                    data = context.get('data', {})
                    response = await client.post(url, json=data, headers=headers)
                else:
                    logger.error(f"Unsupported HTTP method: {method}")
                    return None
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Use LLM to extract answer from API response
                    answer = await self.llm_client.analyze_text(
                        prompt=task_description,
                        context=f"API Response:\n{content}"
                    )
                    
                    return answer
                else:
                    logger.error(f"API request failed: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error in API handler: {e}")
            return None


class VisualizationHandler(TaskHandler):
    """Handler for visualization tasks."""
    
    async def handle(self, task_description: str, context: Dict[str, Any]) -> Any:
        """Generate visualizations."""
        try:
            import matplotlib.pyplot as plt
            import io
            import base64
            
            data = context.get('data')
            chart_type = context.get('chart_type', 'bar')
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Generate chart based on type
            if chart_type == 'bar':
                if isinstance(data, dict):
                    ax.bar(data.keys(), data.values())
            elif chart_type == 'line':
                if isinstance(data, dict):
                    ax.plot(list(data.keys()), list(data.values()))
            
            ax.set_title(context.get('title', 'Chart'))
            ax.set_xlabel(context.get('xlabel', 'X'))
            ax.set_ylabel(context.get('ylabel', 'Y'))
            
            # Save to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            
            # Return as data URI
            return f"data:image/png;base64,{image_base64}"
        except Exception as e:
            logger.error(f"Error in visualization: {e}")
            return None


class GeneralTaskHandler(TaskHandler):
    """General handler for tasks that don't fit other categories."""
    
    async def handle(self, task_description: str, context: Dict[str, Any]) -> Any:
        """Handle general tasks using LLM."""
        try:
            # Combine all context into a string
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items() if v])
            
            answer = await self.llm_client.analyze_text(
                prompt=task_description,
                context=context_str if context_str else None
            )
            
            return answer
        except Exception as e:
            logger.error(f"Error in general task handler: {e}")
            return None
