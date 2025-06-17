from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração da API Key
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("A variável de ambiente API_KEY não foi definida.")
genai.configure(api_key=api_key)

# Configurações do modelo
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# =================================================================
# ||                 INÍCIO DA CORREÇÃO ADICIONADA                 ||
# =================================================================

# Rota principal para verificar se a API está no ar
@app.route('/')
def home():
    """
    Esta é a rota principal. Ela responde ao erro 404 e mostra
    que o serviço está funcionando.
    """
    return jsonify({
        "status": "online",
        "message": "API da Lorena está no ar. Use o endpoint /api/lorena via POST."
    }), 200

# =================================================================
# ||                  FIM DA CORREÇÃO ADICIONADA                   ||
# =================================================================


# Rota da API (seu código original)
@app.route('/api/lorena', methods=['POST'])
def api_lorena():
    data = request.json
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt não fornecido"}), 400

    prompt_text = data['prompt']

    try:
        convo = model.start_chat(history=[])
        convo.send_message(prompt_text)
        return jsonify({"response": convo.last.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # A linha abaixo é útil para testes locais, mas não é usada pela Render.
    # A Render usa o comando gunicorn que você especificou.
    app.run(debug=True)
