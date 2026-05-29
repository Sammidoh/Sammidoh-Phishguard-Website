import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    print("❌ No GROQ_API_KEY found in .env file")
    exit(1)

client = Groq(api_key=api_key)

prompt = """Analyze this URL: http://paypal-verify.com
Return ONLY a valid JSON object with two fields:
- "score": integer from 0 to 100 (0 = safe, 100 = extremely dangerous phishing/malware)
- "reason": a short one-sentence explanation (max 20 words)

Example output: {"score": 95, "reason": "Typosquatting of PayPal domain"}
Do not include any other text, only the JSON object."""

try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a security classifier. Your answer must be ONLY a JSON object. No other text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=100
    )
    content = response.choices[0].message.content.strip()
    print("Raw response:", content)
    # Try to parse JSON
    result = json.loads(content)
    print("✅ Parsed JSON:", result)
except Exception as e:
    print(f"❌ Error: {e}")