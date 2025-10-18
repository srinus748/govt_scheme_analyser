# services/html_extract_service.py
import requests
from readability import Document
from bs4 import BeautifulSoup
import os
import certifi
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time

def extract_text_from_url(url: str) -> str:
    """
    Enhanced content extraction with multiple fallback strategies.
    """
    print(f"Attempting to extract content from: {url}")
    
    # Try multiple extraction methods in order
    methods = [
        ("Selenium with JavaScript", _extract_with_selenium),
        ("Requests + Readability", _extract_with_requests),
        ("Basic Requests", _extract_basic)
    ]
    
    for method_name, method_func in methods:
        try:
            print(f"Trying method: {method_name}")
            content = method_func(url)
            if content and len(content) > 200:  # Minimum content threshold
                print(f"Successfully extracted content using {method_name}")
                return content
            else:
                print(f"Method {method_name} returned insufficient content")
        except Exception as e:
            print(f"Method {method_name} failed: {e}")
            continue
    
    return "Error: Could not extract sufficient text from the URL. The page might require JavaScript, have anti-bot protection, or be inaccessible."

# In services/html_extract_service.py

def _extract_with_selenium(url: str) -> str:
    """Extract content using Selenium for JavaScript-heavy pages."""
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
        
        # Add these options to handle potential blocking
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Load the page
            driver.get(url)
            
            # Wait longer for page to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(5)
            
            # Try to scroll to load more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Get page source
            page_source = driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Try to find main content areas
            main_content = None
            content_selectors = [
                'main', 'article', '[role="main"]', 
                '.content', '.main-content', '#content',
                '.scheme-content', '.page-content', '.container'
            ]
            
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback to body content
                text = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            return cleaned_text
            
        finally:
            driver.quit()
            
    except WebDriverException as e:
        print(f"Selenium WebDriver error: {e}")
        return None
    except Exception as e:
        print(f"Selenium extraction error: {e}")
        return None
def _extract_with_requests(url: str) -> str:
    """Extract content using requests + readability."""
    try:
        ssl_verify = os.getenv("SSL_VERIFY", "True").lower() == "true"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        response = requests.get(url, headers=headers, timeout=30, verify=certifi.where() if ssl_verify else False)
        response.raise_for_status()
        
        # Try readability first
        doc = Document(response.content)
        html_content = doc.summary()
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_text = soup.get_text(separator='\n', strip=True)
        
        if len(extracted_text) > 200:
            return extracted_text
        else:
            # Fallback to basic extraction
            return _extract_basic_fallback(response.content)
            
    except Exception as e:
        print(f"Requests extraction error: {e}")
        return None

def _extract_basic(url: str) -> str:
    """Basic extraction without readability."""
    try:
        ssl_verify = os.getenv("SSL_VERIFY", "True").lower() == "true"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=30, verify=certifi.where() if ssl_verify else False)
        response.raise_for_status()
        
        return _extract_basic_fallback(response.content)
        
    except Exception as e:
        print(f"Basic extraction error: {e}")
        return None

def _extract_basic_fallback(content: bytes) -> str:
    """Basic BeautifulSoup extraction fallback."""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header']):
        element.decompose()
    
    # Try to find main content
    main_content = (
        soup.find('main') or 
        soup.find('article') or 
        soup.find('div', class_=re.compile(r'content|main', re.I)) or
        soup.find('div', id=re.compile(r'content|main', re.I))
    )
    
    if main_content:
        text = main_content.get_text(separator='\n', strip=True)
    else:
        text = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
    
    # Clean up text
    lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 3]
    return '\n'.join(lines)

def extract_with_playwright(url: str) -> str:
    """Alternative extraction using Playwright (if available)."""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Set user agent
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            # Navigate and wait
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Extract text
            text = page.evaluate("""
                () => {
                    // Remove unwanted elements
                    const elements = document.querySelectorAll('script, style, nav, footer, header');
                    elements.forEach(el => el.remove());
                    
                    // Try to find main content
                    const main = document.querySelector('main, article, [role="main"], .content, .main-content') || document.body;
                    return main.innerText || '';
                }
            """)
            
            browser.close()
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)
            
    except ImportError:
        print("Playwright not installed")
        return None
    except Exception as e:
        print(f"Playwright extraction error: {e}")
        return None