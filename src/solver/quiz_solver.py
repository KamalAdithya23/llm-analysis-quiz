"""Main quiz solver orchestrator."""

import asyncio
import re
import json
from typing import Optional, Dict, Any
from pathlib import Path
import httpx
from bs4 import BeautifulSoup

from src.utils.logger import logger
from src.utils.helpers import Timer, get_payload_size
from src.config import settings
from src.solver.browser_handler import BrowserHandler
from src.solver.llm_client import LLMClient
from src.solver.task_handlers import (
    DataScrapingHandler,
    PDFProcessingHandler,
    DataAnalysisHandler,
    APIHandler,
    VisualizationHandler,
    GeneralTaskHandler
)
from src.api.models import SubmitRequest, SubmitResponse


class QuizSolver:
    """Main orchestrator for solving quiz tasks."""
    
    def __init__(self):
        """Initialize quiz solver."""
        self.llm_client = LLMClient()
        self.handlers = {
            'scraping': DataScrapingHandler(),
            'pdf': PDFProcessingHandler(),
            'analysis': DataAnalysisHandler(),
            'api': APIHandler(),
            'visualization': VisualizationHandler(),
            'general': GeneralTaskHandler()
        }
    
    async def solve_quiz_chain(self, initial_url: str, email: str, secret: str):
        """
        Solve a chain of quiz tasks.
        
        Args:
            initial_url: Starting quiz URL
            email: User email
            secret: User secret
        """
        current_url = initial_url
        quiz_count = 0
        
        with Timer(timeout_seconds=settings.timeout_seconds) as timer:
            while current_url and not timer.is_timeout():
                quiz_count += 1
                logger.info(f"Solving quiz #{quiz_count}: {current_url}")
                logger.info(f"Time remaining: {timer.remaining():.1f}s")
                
                # Solve the quiz
                next_url = await self.solve_single_quiz(
                    quiz_url=current_url,
                    email=email,
                    secret=secret,
                    time_remaining=timer.remaining()
                )
                
                if next_url:
                    current_url = next_url
                else:
                    logger.info("Quiz chain completed or no more URLs")
                    break
            
            if timer.is_timeout():
                logger.warning("Quiz chain timed out")
            else:
                logger.info(f"Successfully completed {quiz_count} quizzes")
    
    async def solve_single_quiz(
        self,
        quiz_url: str,
        email: str,
        secret: str,
        time_remaining: float
    ) -> Optional[str]:
        """
        Solve a single quiz task.
        
        Args:
            quiz_url: Quiz URL
            email: User email
            secret: User secret
            time_remaining: Time remaining in seconds
            
        Returns:
            Next quiz URL if available, None otherwise
        """
        try:
            # Step 1: Fetch and parse quiz page
            quiz_data = await self.fetch_quiz_page(quiz_url)
            if not quiz_data:
                logger.error("Failed to fetch quiz page")
                return None
            
            # Step 2: Parse task and extract information
            task_info = await self.parse_quiz_task(quiz_data)
            if not task_info:
                logger.error("Failed to parse quiz task")
                return None
            
            logger.info(f"Task: {task_info.get('task_description', 'Unknown')[:100]}")
            
            # Step 3: Solve the task
            answer = await self.solve_task(task_info)
            if answer is None:
                logger.error("Failed to solve task")
                return None
            
            logger.info(f"Answer: {str(answer)[:200]}")
            
            # Step 4: Submit answer
            submit_url = task_info.get('submit_url')
            if not submit_url:
                logger.error("No submit URL found")
                return None
            
            response = await self.submit_answer(
                submit_url=submit_url,
                email=email,
                secret=secret,
                quiz_url=quiz_url,
                answer=answer
            )
            
            if response:
                if response.correct:
                    logger.info("Answer was CORRECT!")
                else:
                    logger.warning(f"Answer was INCORRECT: {response.reason}")
                
                return response.url  # Next URL or None
            
            return None
        except Exception as e:
            logger.error(f"Error solving quiz: {e}", exc_info=True)
            return None
    
    async def fetch_quiz_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and render quiz page.
        
        Args:
            url: Quiz URL
            
        Returns:
            Dictionary with page content and metadata
        """
        try:
            async with BrowserHandler() as browser:
                success = await browser.navigate_to(url)
                if not success:
                    return None
                
                # Extract quiz instructions
                content = await browser.extract_quiz_instructions()
                if not content:
                    return None
                
                # Get full HTML for link extraction
                full_html = await browser.get_page_content()
                
                return {
                    'content': content,
                    'html': full_html,
                    'url': url
                }
        except Exception as e:
            logger.error(f"Error fetching quiz page: {e}")
            return None
    
    async def parse_quiz_task(self, quiz_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse quiz task to extract instructions, data sources, and submit URL.
        
        Args:
            quiz_data: Quiz page data
            
        Returns:
            Dictionary with task information
        """
        try:
            content = quiz_data['content']
            html = quiz_data['html']
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Find submit URL
            submit_url = None
            submit_match = re.search(r'https?://[^\s<>"]+/submit[^\s<>"]*', content)
            if submit_match:
                submit_url = submit_match.group(0)
            
            # Find data file URLs
            file_urls = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href for ext in ['.pdf', '.csv', '.json', '.xlsx', '.txt']):
                    file_urls.append(href)
            
            # Use LLM to understand the task
            task_description = await self.llm_client.analyze_text(
                prompt="Extract the main question or task from this quiz. Be concise and specific.",
                context=text_content
            )
            
            return {
                'task_description': task_description or text_content,
                'raw_content': text_content,
                'submit_url': submit_url,
                'file_urls': file_urls,
                'html': html
            }
        except Exception as e:
            logger.error(f"Error parsing quiz task: {e}")
            return None
    
    async def solve_task(self, task_info: Dict[str, Any]) -> Any:
        """
        Solve the quiz task using appropriate handler.
        
        Args:
            task_info: Task information
            
        Returns:
            Answer to the task
        """
        try:
            task_description = task_info['task_description']
            raw_content = task_info['raw_content']
            file_urls = task_info.get('file_urls', [])
            
            # Download files if any
            downloaded_files = []
            if file_urls:
                for file_url in file_urls:
                    file_path = await self.download_file(file_url)
                    if file_path:
                        downloaded_files.append(file_path)
            
            # Determine task type and use appropriate handler
            context = {
                'task': task_description,
                'content': raw_content,
                'files': downloaded_files
            }
            
            # Check if PDF processing is needed
            if downloaded_files and any(str(f).endswith('.pdf') for f in downloaded_files):
                pdf_file = next(f for f in downloaded_files if str(f).endswith('.pdf'))
                
                # Extract page number if mentioned
                page_match = re.search(r'page\s+(\d+)', raw_content, re.IGNORECASE)
                page_num = int(page_match.group(1)) if page_match else None
                
                return await self.handlers['pdf'].handle(
                    task_description,
                    {'pdf_path': pdf_file, 'page_number': page_num}
                )
            
            # Check if CSV/data analysis is needed
            elif downloaded_files and any(str(f).endswith(('.csv', '.json')) for f in downloaded_files):
                data_file = downloaded_files[0]
                data_type = 'csv' if str(data_file).endswith('.csv') else 'json'
                
                return await self.handlers['analysis'].handle(
                    task_description,
                    {'data': str(data_file), 'data_type': data_type}
                )
            
            # Use general handler for other tasks
            else:
                return await self.handlers['general'].handle(
                    task_description,
                    context
                )
        except Exception as e:
            logger.error(f"Error solving task: {e}")
            return None
    
    async def download_file(self, url: str) -> Optional[Path]:
        """
        Download a file from URL.
        
        Args:
            url: File URL
            
        Returns:
            Path to downloaded file or None
        """
        try:
            # Create downloads directory
            download_dir = Path("downloads")
            download_dir.mkdir(exist_ok=True)
            
            # Extract filename
            filename = url.split('/')[-1].split('?')[0]
            file_path = download_dir / filename
            
            # Download using browser handler
            async with BrowserHandler() as browser:
                success = await browser.download_file(url, str(file_path))
                if success:
                    return file_path
            
            return None
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    async def submit_answer(
        self,
        submit_url: str,
        email: str,
        secret: str,
        quiz_url: str,
        answer: Any
    ) -> Optional[SubmitResponse]:
        """
        Submit answer to the quiz endpoint.
        
        Args:
            submit_url: Submission endpoint URL
            email: User email
            secret: User secret
            quiz_url: Original quiz URL
            answer: Answer to submit
            
        Returns:
            SubmitResponse or None
        """
        try:
            # Prepare payload
            payload = {
                "email": email,
                "secret": secret,
                "url": quiz_url,
                "answer": answer
            }
            
            # Check payload size
            payload_size = get_payload_size(payload)
            if payload_size > settings.max_payload_size:
                logger.error(f"Payload too large: {payload_size} bytes")
                return None
            
            logger.info(f"Submitting answer to {submit_url}")
            logger.info(f"Payload size: {payload_size} bytes")
            
            # Submit
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(submit_url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    return SubmitResponse(**data)
                else:
                    logger.error(f"Submit failed: HTTP {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return None
