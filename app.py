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

    # Remove markdown code fences (```json ... ``` or ``` ... ```)
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the outermost { ... } block in case AI added surrounding text
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
            return None, []

        context_lines = []
        for r in results:
            context_lines.append(f"- {r['title']}: {r['body']}")

        return "\n".join(context_lines), results
    except Exception as e:
        print(f"Search error: {e}")
        return None, []


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


@app.route('/api/explain', methods=['POST'])
def explain():
    data = request.get_json()
    policy = (data.get('policy') or '').strip()
    user_type = data.get('userType', 'general')
    language = data.get('language', 'hinglish')

    if not policy:
        return jsonify({'error': 'Policy name is required'}), 400

    user_label = USER_TYPE_LABELS.get(user_type, 'General Citizen')
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS['hinglish'])

    # Step 1: Fetch real-time web context
    web_context, raw_results = fetch_web_context(policy)

    if web_context:
        context_block = f"""
REAL-TIME WEB SEARCH RESULTS for "{policy}":
{web_context}

Use the above search results as your primary source of truth. Base your answer on this current information.
"""
    else:
        context_block = f"""
No web search results were found for "{policy}".
If this policy clearly does not exist or is not a real government policy, set "invalid" to true.
Otherwise, use your training knowledge carefully.
"""

    prompt = f"""You are an expert on government policies, especially Indian government policies.

{context_block}

Now explain the policy "{policy}" for a {user_label} in {lang_instruction}

VALIDATION RULES (be very generous — only reject obvious nonsense):
- Mark "invalid" ONLY if the input is complete gibberish like "asdfjkl policy" or "xyz 9999 bill" with zero connection to any real policy or topic.
- Real bills, acts, schemes, budgets, reservations, amendments — even if search results are limited — should ALWAYS be answered using your training knowledge.
- If the policy is a future proposal, explain what is known or proposed about it. Do NOT reject it.
- When in doubt, ANSWER. Never reject a real-sounding policy name.

If valid, return ONLY this JSON (no markdown, no extra text):
{{
  "invalid": false,
  "simple_explanation": "3-4 sentences explaining what this policy is based on current information.",
  "why_introduced": "2-3 sentences about why the government introduced or proposed this policy.",
  "personal_impact": "3-4 sentences on how this policy specifically affects a {user_label}. Be concrete.",
  "pros": ["benefit 1", "benefit 2", "benefit 3"],
  "cons": ["drawback 1", "drawback 2", "drawback 3"],
  "summary": "Exactly 2 lines. Key takeaway for a {user_label}."
}}

CRITICAL RULES:
- Keep all JSON keys in English exactly as shown above (e.g., "simple_explanation", "pros", "cons")
- Write only the VALUES in {lang_instruction.split('—')[0].strip()}
- Return raw JSON only — no extra sentences, no markdown, no explanation outside the JSON"""

    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            max_tokens=1500,
            messages=[
                {
                    'role': 'system',
                    'content': 'You explain government policies using real web search data. Always respond with valid JSON only. No markdown, no extra text.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        text = response.choices[0].message.content.strip()
        print(f"[AI RAW RESPONSE]:\n{text}\n")  # debug log

        parsed = extract_json(text)

        if parsed is None:
            return jsonify({'error': 'Could not parse AI response. Please try again.'}), 500

        if parsed.get('invalid'):
            return jsonify({'error': parsed.get('reason', 'This policy does not exist or could not be found.')}), 422

        return jsonify({'result': parsed})

    except json.JSONDecodeError:
        return jsonify({'error': 'Could not parse AI response. Please try again.'}), 500
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'\nPolicyLens AI running at http://localhost:{port}\n')
    app.run(port=port, debug=True)
