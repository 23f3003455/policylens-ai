from flask import Blueprint, request, jsonify

from .ai import explain_policy

api_bp = Blueprint('api', __name__)


@api_bp.route('/explain', methods=['POST'])
def explain():
    data = request.get_json()
    policy = (data.get('policy') or '').strip()
    user_type = data.get('userType', 'general')
    language = data.get('language', 'hinglish')

    if not policy or len(policy) < 3:
        return jsonify({'error': 'Please enter a valid policy name.'}), 400

    try:
        result = explain_policy(policy, user_type, language)
        return jsonify({'result': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500
