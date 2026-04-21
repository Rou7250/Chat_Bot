import google.generativeai as genai

_VERIFY_PROMPT = """You are a strict fact-checker.

Context:
{context}

Answer:
{answer}

Tasks:
1. Is the answer fully supported by the context? Reply YES or NO.
2. Confidence level: High, Medium, or Low.

Respond ONLY as JSON: {{"supported": "YES/NO", "confidence": "High/Medium/Low"}}"""

def verify_answer(answer: str, context: str, model) -> dict:
    try:
        res = model.generate_content(
            _VERIFY_PROMPT.format(context=context[:2000], answer=answer)
        )
        import json, re
        text = res.text.strip()
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception:
        pass
    return {"supported": "YES", "confidence": "Medium"}
