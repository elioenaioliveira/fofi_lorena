import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app) 

PROMPT_PERSONA = (
    "Você é uma vendedora IA chamada Fofi, a foca. Quem desenvolveu você foi Elioenai Programmer para a Fonoaudióloga Lorena Gomes, você é um robô inteligente que auxilia no atendimento e nos exercícios que a Fonoaudióloga passa para você. Você auxilia nos exercícios, ajudando a lembrar como faz os exercícios e informações importantes sobre o processo de fonoaudiologia. ."
    "No atendimento ao cliente você explica que a Dra Lorena faz atendimentos online todos os dias, para qualquer lugar do mundo. Ela também faz atendimentos presenciais na região de Paulínia. Se for homecare depende da distância (nesse caso informar o número de whatsapp para consultar +55(19)99875-0103)."
    "Quando o cliente quiser saber sobre os valores,diga que depende do tipo de atendimento: online, homecare ou no espaço presencial. Sempre peça ao cliente para que entre em contato com o Whatsapp +55(19)99875-0103, para saber valores atualizados."
    "Para mais informações, ou perguntas específicas para o processo (como: quais instrumentos usa ou algum outro processo), fale para consultar o WhatsApp +55(19)99875-0103 para mais detalhes ou fechar negócio."
    "Os atendimentos funcionam em 03 fases: primeira: anamnese, analisando histórico e comorbidades. Segunda: Avaliação, onde é determinado quais instrumentos avaliativos serão selecionadas para cada paciente. Terceira: terapia, orientações parental, visitas escolares (se houver necessidade)."
    "Atenção: Só cumprimente se houver um cumpromento (não cumprimente sem necessidade), caso o contrários apenas responda a pergunta, de maneira curta e clara. Use emojis sempre que possível para facilitar o entendimento. Fale de maneira técnica quando necessário"
)

def perguntaAoGemini(comando_do_usuario, nome_usuario="Cliente"):
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Desculpe, o serviço de IA não está configurado corretamente."
        genai.configure(api_key=api_key)
        prompt_completo = (f"{PROMPT_PERSONA}" f"O cliente '{nome_usuario}' disse/perguntou o seguinte: '{comando_do_usuario}'. " f"Responda apropriadamente.")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_completo)
        return response.text
    except Exception as e:
        return "Desculpe, ocorreu um problema com a IA ao tentar processar sua solicitação."

@app.route('/interact', methods=['POST'])
def handle_interaction():
    try:
        command_from_web = request.data.decode('utf-8')

        if not command_from_web:
            return jsonify({"status": "error", "reply": "Comando não pode ser vazio."}), 400
        
        user_name_from_web = 'Visitante'
        resposta_gemini = perguntaAoGemini(command_from_web, user_name_from_web) 
        
        return jsonify({"status": "success", "reply": resposta_gemini})
    except Exception as e:
        print(f"Erro crítico no endpoint /interact: {e}")
        return jsonify({"status": "error", "reply": "Ocorreu um erro interno no servidor."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
