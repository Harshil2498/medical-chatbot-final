# app/services/llm_service.py
import requests
import json
from typing import Iterator, Optional, List


class OllamaLLMService:
    """Interface to Ollama for LLM"""
    
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name
        print(f"🤖 Initializing Ollama with model: {model_name}...")
        
        if self.check_health():
            print("✅ Ollama is running!")
        else:
            print("⚠️  WARNING: Ollama is not responding! Make sure 'ollama serve' is running.")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        stop_sequences: Optional[List[str]] = None
    ) -> str:
        """Generate text from prompt"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "stop": stop_sequences or []
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be processing a complex query."
        except Exception as e:
            print(f"❌ Error calling Ollama: {e}")
            return f"Error: Unable to generate response. Please ensure Ollama is running."
    
    def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Iterator[str]:
        """Stream completion from Ollama"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'response' in chunk:
                        yield chunk['response']
        except Exception as e:
            print(f"❌ Stream error: {e}")
            yield f"Error: {str(e)}"
    
    def check_health(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False