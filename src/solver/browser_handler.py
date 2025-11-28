"""Browser automation handler using Playwright."""

import asyncio
import base64
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from pathlib import Path

from src.utils.logger import logger


class BrowserHandler:
    """Handles browser automation for quiz page rendering and interaction."""
    
    def __init__(self):
        """Initialize browser handler."""
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, *args):
        """Async context manager exit."""
        await self.close()
    
    async def start(self):
        """Start the browser."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = await self.context.new_page()
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    async def close(self):
        """Close the browser."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def navigate_to(self, url: str, wait_for: str = 'networkidle') -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_for: Wait condition ('load', 'domcontentloaded', 'networkidle')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Navigating to {url}")
            await self.page.goto(url, wait_until=wait_for, timeout=30000)
            # Wait a bit for any dynamic content
            await asyncio.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    async def get_page_content(self) -> str:
        """
        Get the full HTML content of the current page.
        
        Returns:
            HTML content as string
        """
        try:
            content = await self.page.content()
            return content
        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            return ""
    
    async def get_text_content(self, selector: str = "body") -> str:
        """
        Get text content from a specific element.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            Text content
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                text = await element.text_content()
                return text or ""
            return ""
        except Exception as e:
            logger.error(f"Failed to get text content for {selector}: {e}")
            return ""
    
    async def get_inner_html(self, selector: str) -> str:
        """
        Get inner HTML of an element.
        
        Args:
            selector: CSS selector
            
        Returns:
            Inner HTML content
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                html = await element.inner_html()
                return html or ""
            return ""
        except Exception as e:
            logger.error(f"Failed to get inner HTML for {selector}: {e}")
            return ""
    
    async def extract_quiz_instructions(self) -> Optional[str]:
        """
        Extract quiz instructions from the page.
        Handles base64 encoded content.
        
        Returns:
            Decoded quiz instructions or None
        """
        try:
            # Wait for result div to be populated
            await self.page.wait_for_selector("#result", timeout=10000)
            
            # Get the content
            content = await self.get_inner_html("#result")
            
            if not content:
                # Try getting text content from body
                content = await self.get_text_content("body")
            
            logger.info(f"Extracted quiz content (length: {len(content)})")
            return content
        except Exception as e:
            logger.error(f"Failed to extract quiz instructions: {e}")
            return None
    
    async def download_file(self, url: str, output_path: str) -> bool:
        """
        Download a file from a URL.
        
        Args:
            url: File URL
            output_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading file from {url}")
            
            # Navigate to the URL
            response = await self.page.goto(url, wait_until='networkidle')
            
            if response and response.ok:
                # Get the content
                content = await response.body()
                
                # Save to file
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(content)
                
                logger.info(f"File downloaded successfully to {output_path}")
                return True
            else:
                logger.error(f"Failed to download file: HTTP {response.status if response else 'No response'}")
                return False
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False
    
    async def take_screenshot(self, output_path: str) -> bool:
        """
        Take a screenshot of the current page.
        
        Args:
            output_path: Path to save screenshot
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            await self.page.screenshot(path=output_path, full_page=True)
            logger.info(f"Screenshot saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    async def execute_javascript(self, script: str) -> Any:
        """
        Execute JavaScript on the page.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Result of the script execution
        """
        try:
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {e}")
            return None
