import os
import json
from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
from dotenv import load_dotenv

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

    prompt = f"""You are an expert on Indian government policies. Explain the following policy in {lang_instruction}

Policy to explain: "{policy}"
Target user: {user_label}

Return ONLY a valid JSON object with exactly these keys (no markdown, no extra text):
{{
  "simple_explanation": "3-4 sentences explaining what this policy is. Use simple everyday language.",
  "why_introduced": "2-3 sentences about why the government introduced this policy.",
  "personal_impact": "3-4 sentences explaining specifically how this policy affects a {user_label}. Be concrete and relatable.",
  "pros": ["benefit 1", "benefit 2", "benefit 3"],
  "cons": ["drawback 1", "drawback 2", "drawback 3"],
  "summary": "Exactly 2 lines. Key takeaway for a {user_label}."
}}

IMPORTANT: Write ALL values in the JSON in {lang_instruction.split('—')[0].strip()}. Do not use English unless the language is Hinglish."""

    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            max_tokens=1500,
            messages=[
                {
                    'role': 'system',
                    'content': 'You explain Indian government policies in regional Indian languages. Always respond with valid JSON only. No markdown, no extra text.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        text = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if text.startswith('```'):
            parts = text.split('```')
            text = parts[1].lstrip('json').strip() if len(parts) > 1 else text

        parsed = json.loads(text)
        return jsonify({'result': parsed})

    except json.JSONDecodeError:
        return jsonify({'error': 'Could not parse AI response. Please try again.'}), 500
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'\n🔍 PolicyLens AI running at http://localhost:{port}\n')
    app.run(port=port, debug=True)
