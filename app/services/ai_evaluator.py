from typing import List, Dict, Any, Tuple
import httpx
from app.config import settings

class AIEvaluator:
    @staticmethod
    def score_response(expected_facts: List[str], answer_text: str) -> Tuple[int, str]:
        """
        Blueprint Section 10 scoring:
        2 = fully correct
        1 = partly correct or incomplete
        0 = wrong or missing
        """
        if not answer_text or not answer_text.strip():
            return 0, "No answer received or blank text."
            
        answer_lower = answer_text.lower()
        matched = []
        missing = []
        
        for fact in expected_facts:
            # Check either direct substring or all significant tokens present
            tokens = [t.strip().lower() for t in fact.replace("-", " ").split() if len(t.strip()) > 1]
            if not tokens:
                tokens = [fact.strip().lower()]
            
            # If all key tokens of the expected fact appear in the answer
            if fact.lower() in answer_lower or all(token in answer_lower for token in tokens):
                matched.append(fact)
            else:
                missing.append(fact)
                
        total = len(expected_facts)
        if total == 0:
            return 2, "No specific facts required."
            
        match_ratio = len(matched) / total
        
        if match_ratio >= 0.7:
            score = 2
            notes = f"Verified {len(matched)}/{total} facts accurately."
        elif match_ratio >= 0.3:
            score = 1
            notes = f"Partially accurate ({len(matched)}/{total} facts found). Missing: {', '.join(missing)}."
        else:
            score = 0
            notes = f"Failed to identify key verified facts. Missing: {', '.join(missing)}."
            
        return score, notes

    @staticmethod
    async def query_model_api(platform_name: str, question: str) -> Tuple[str, str]:
        """
        Call live platform API if key is present, else provide instructions for manual benchmarking.
        """
        platform = platform_name.lower()
        
        if "gemini" in platform and settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {"contents": [{"parts": [{"text": question}]}]}
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return text, "Gemini 1.5 Flash"
            except Exception as e:
                return f"API Query Error: {str(e)}", "Gemini API Error"

        elif "chatgpt" in platform and settings.OPENAI_API_KEY:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": question}],
                    "temperature": 0.2
                }
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"]
                        return text, "GPT-4o-mini"
            except Exception as e:
                return f"API Query Error: {str(e)}", "OpenAI API Error"
                
        # Default placeholder / manual entry instruction
        return f"[Manual Benchmark Result for {platform_name}]\nPlatform was tested on question: '{question}'. Add the actual platform response here.", "Manual Review"
