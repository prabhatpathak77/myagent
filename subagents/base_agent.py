import google.generativeai as genai
from config import GOOGLE_API_KEY
import time


class BaseAgent:
    """Base class for all subagents"""
    
    def __init__(self, name, role):
        self.name = name
        self.role = role
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash-lite',
            generation_config={
                'temperature': 0.7,
            }
        )
        self.request_timeout = 30  # seconds
    
    def process(self, task):
        """Process a task - to be implemented by subagents"""
        raise NotImplementedError("Subagents must implement process method")
    
    def generate_with_retry(self, prompt, max_retries=3):
        """Generate content with retry logic for timeout and rate limit errors"""
        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e)
                # Handle rate limits (429) and timeouts (504)
                if '429' in error_msg or 'rate' in error_msg.lower() or 'quota' in error_msg.lower() or 'exhausted' in error_msg.lower():
                    if attempt < max_retries:
                        wait_time = (attempt + 1) * 5  # longer wait for rate limits
                        print(f"[{self.name}] Rate limit hit, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("Rate limit exceeded. Please wait a moment and try again.")
                elif 'deadline' in error_msg.lower() or 'timeout' in error_msg.lower() or '504' in error_msg:
                    if attempt < max_retries:
                        wait_time = (attempt + 1) * 2
                        print(f"[{self.name}] Timeout on attempt {attempt + 1}, retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                raise e
        raise Exception(f"Failed after {max_retries + 1} attempts")
    
    def report_to_coordinator(self, result):
        """Report results back to coordinator"""
        return {
            'agent': self.name,
            'status': 'completed',
            'result': result
        }
