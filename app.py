import os
from flask import Flask, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='public')

from api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'\nPolicyLens AI running at http://localhost:{port}\n')
    app.run(port=port, debug=True)
