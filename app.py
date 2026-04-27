import os
import re
import json
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

app = Flask(__name__, static_folder='public')
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

USER_TYPE_LABELS = {
    'student': 'Student',
    'job_seeker': 'Job Seeker',
    'business_owner': 'Business Owner',
    'general': 'General Citizen',
}

LANGUAGE_INSTRUCTIONS = {
    'hinglish':  'Hinglish — natural mix of Hindi and English as urban Indians speak (e.g., "Yeh policy basically tax ko simplify karti hai"). Use Devanagari script for Hindi words mixed with English.',
    'hindi':     'pure Hindi using Devanagari script. Avoid English words where a Hindi equivalent exists.',
    'bengali':   'Bengali (বাংলা) using Bengali script. Write naturally as a Bengali speaker would explain it.',
    'telugu':    'Telugu (తెలుగు) using Telugu script. Write naturally as a Telugu speaker would explain it.',
    'marathi':   'Marathi (मराठी) using Devanagari script. Write naturally as a Marathi speaker would explain it.',
    'tamil':     'Tamil (தமிழ்) using Tamil script. Write naturally as a Tamil speaker would explain it.',
    'gujarati':  'Gujarati (ગુજરાતી) using Gujarati script. Write naturally as a Gujarati speaker would explain it.',
    'kannada':   'Kannada (ಕನ್ನಡ) using Kannada script. Write naturally as a Kannada speaker would explain it.',
    'malayalam': 'Malayalam (മലയാളം) using Malayalam script. Write naturally as a Malayalam speaker would explain it.',
    'punjabi':   'Punjabi (ਪੰਜਾਬੀ) using Gurmukhi script. Write naturally as a Punjabi speaker would explain it.',
    'odia':      'Odia (ଓଡ଼ିଆ) using Odia script. Write naturally as an Odia speaker would explain it.',
}


def extract_json(text):
    """Robustly extract a JSON object from AI response text."""
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def fetch_web_context(policy):
    """Search DuckDuckGo and return top results as a context string."""
    try:
        results = DDGS().text(
            f"{policy} India government bill act scheme",
            max_results=6
        )
        if not results:
            return None
        return "\n".join(f"- {r['title']}: {r['body']}" for r in results)
    except Exception as e:
        print(f"Search error: {e}")
        return None


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/api/explain', methods=['POST'])
def explain():
    data = request.get_json()
    policy = (data.get('policy') or '').strip()
    user_type = data.get('userType', 'general')
    language = data.get('language', 'hinglish')

    if not policy or len(policy) < 3:
        return jsonify({'error': 'Please enter a valid policy name.'}), 400

    user_label = USER_TYPE_LABELS.get(user_type, 'General Citizen')
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS['hinglish'])

    web_context = fetch_web_context(policy)

    if web_context:
        context_block = f"""REAL-TIME WEB SEARCH RESULTS for "{policy}":
{web_context}

Use these search results as your primary source. Base your answer on this current information."""
    else:
        context_block = f"""No web search results found for "{policy}". Use your training knowledge to answer as accurately as possible."""

    prompt = f"""You are an expert on Indian and global government policies.

{context_block}

Explain the policy "{policy}" for a {user_label} in {lang_instruction}

Return ONLY this JSON object (no markdown, no extra text outside the JSON):
{{
  "simple_explanation": "3-4 sentences explaining what this policy is.",
  "why_introduced": "2-3 sentences about why this policy was introduced.",
  "personal_impact": "3-4 sentences on how this specifically affects a {user_label}. Be concrete.",
  "pros": ["benefit 1", "benefit 2", "benefit 3"],
  "cons": ["drawback 1", "drawback 2", "drawback 3"],
  "summary": "Exactly 2 lines. Key takeaway for a {user_label}."
}}

RULES:
- Keep JSON keys exactly as shown in English
- Write all VALUES in {lang_instruction.split('—')[0].strip()}
- Return raw JSON only, no text before or after"""

    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            max_tokens=1500,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a policy expert. Always respond with a valid JSON object only. No markdown, no extra text.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        text = response.choices[0].message.content.strip()
        print(f"[AI RESPONSE]:\n{text}\n")

        parsed = extract_json(text)

        if parsed is None:
            return jsonify({'error': 'Could not parse AI response. Please try again.'}), 500

        return jsonify({'result': parsed})

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'\nPolicyLens AI running at http://localhost:{port}\n')
    app.run(port=port, debug=True)
