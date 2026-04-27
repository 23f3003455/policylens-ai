import os
from groq import Groq

from .constants import USER_TYPE_LABELS, LANGUAGE_INSTRUCTIONS
from .search import fetch_web_context
from .utils import extract_json

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))


def _build_prompt(policy, user_label, lang_instruction, web_context):
    if web_context:
        context_block = (
            f'REAL-TIME WEB SEARCH RESULTS for "{policy}":\n'
            f'{web_context}\n\n'
            'Use these search results as your primary source. Base your answer on this current information.'
        )
    else:
        context_block = (
            f'No web search results found for "{policy}". '
            'Use your training knowledge to answer as accurately as possible.'
        )

    return f"""You are an expert on Indian and global government policies.

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


def explain_policy(policy, user_type, language):
    """
    Fetch web context, call Groq, and return the parsed result dict.
    Raises ValueError if the AI response cannot be parsed.
    Raises Exception on Groq API errors.
    """
    user_label = USER_TYPE_LABELS.get(user_type, 'General Citizen')
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS['hinglish'])

    web_context = fetch_web_context(policy)
    prompt = _build_prompt(policy, user_label, lang_instruction, web_context)

    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        max_tokens=1500,
        messages=[
            {
                'role': 'system',
                'content': 'You are a policy expert. Always respond with a valid JSON object only. No markdown, no extra text.',
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    )

    text = response.choices[0].message.content.strip()
    print(f'[AI RESPONSE]:\n{text}\n')

    parsed = extract_json(text)
    if parsed is None:
        raise ValueError('Could not parse AI response. Please try again.')

    return parsed
