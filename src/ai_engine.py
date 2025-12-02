import os
import json
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AIEngine:
    def __init__(self):
        # User should set this environment variable
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            print("Warning: GEMINI_API_KEY environment variable not set. AI features will return errors.")

    def analyze_complexity(self, ast_subtree: Dict[str, Any]) -> Dict[str, str]:
        """
        Sends the AST subtree to Google Gemini to analyze complexity.
        """
        if not self.api_key:
             return {"O": "Error: Missing API Key", "Omega": "Error", "Theta": "Error"}
        
        prompt = f"""
        You are an expert in Algorithmic Complexity Analysis.
        Analyze the time complexity of the following Abstract Syntax Tree (AST) representing a pseudocode algorithm.
        The AST is provided in JSON format.
        
        Focus on:
        1. Dependent loops (inner loop limits depending on outer loop variables).
        2. Non-linear updates.
        3. Recursive calls.

        Return ONLY a raw JSON object (no markdown formatting, no explanations outside JSON) with the following keys:
        - "O": The Big O complexity (Worst Case).
        - "Omega": The Big Omega complexity (Best Case).
        - "Theta": The Big Theta complexity (Average Case).
        
        Use standard notation like "n^2", "n log n", "1", "n".

        AST:
        {json.dumps(ast_subtree, indent=2)}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean up potential markdown code blocks if the model ignores instructions
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            result = json.loads(text.strip())
            
            # Validate keys
            if not all(k in result for k in ["O", "Omega", "Theta"]):
                return {"O": "Error: Invalid AI Response", "Omega": "Error", "Theta": "Error"}
                
            return result
            
        except Exception as e:
            return {"O": f"Error: {str(e)}", "Omega": "Error", "Theta": "Error"}
