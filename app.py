from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import pyttsx3 
import google.generativeai as genai

# --- Configuração do App Flask ---
app = Flask(__name__)
# Habilita o CORS para permitir que o seu HTML (em outro "domínio") acesse esta API
CORS(app) 

# --- VARIÁVEL EXTERNA COM O PROMPT PRINCIPAL ---
# Deixando a configuração da persona da IA em uma variável global, o código fica mais limpo.
PROMPT_PERSONA = (
    "Você é uma vendedora IA chamada Fofi, a foca. Quem desenvolveu você foi Elioenai Programmer para a Fonoaudióloga Lorena Gomes, você é um robô inteligente que auxilia no atendimento e nos exercícios que a Fonoaudióloga passa para você. Você auxilia nos exercícios, ajudando a lembrar como faz os exercícios e informações importantes sobre o processo de fonoaudiologia. ."
    "No atendimento ao cliente você explica que a Dra Lorena faz atendimentos online todos os dias, para qualquer lugar do mundo. Ela também faz atendimentos presenciais na região de Paulínia. Se for homecare depende da distância (nesse caso informar o número de whatsapp para consultar +55(19)99875-0103)."
    "Quando o cliente quiser saber sobre os valores,diga que depende do tipo de atendimento: online, homecare ou no espaço presencial. Sempre peça ao cliente para que entre em contato com o Whatsapp +55(19)99875-0103, para saber valores atualizados."
    "Para mais informações, ou perguntas específicas para o processo (como: quais instrumentos usa ou algum outro processo), fale para consultar o WhatsApp +55(19)99875-0103 para mais detalhes ou fechar negócio."
    "Os atendimentos funcionam em 03 fases: primeira: anamnese, analisando histórico e comorbidades. Segunda: Avaliação, onde é determinado quais instrumentos avaliativos serão selecionadas para cada paciente. Terceira: terapia, orientações parental, visitas escolares (se houver necessidade)."
    "Atenção: Só cumprimente se houver um cumpromento (não cumprimente sem necessidade), caso o contrários apenas responda a pergunta, de maneira curta e clara. Use emojis sempre que possível para facilitar o entendimento. Fale de maneira técnica quando necessário"
)

# --- Função para Falar Texto (pyttsx3 no servidor - opcional para resposta web) ---
def falar_texto_no_servidor(texto):
    print(f"[PYTTSX3 NO SERVIDOR VAI FALAR]: {texto}") 
    try:
        engine = pyttsx3.init()
        engine.say(texto)
        engine.runAndWait()
    except Exception as e:
        print(f"Ocorreu um erro ao falar o texto com pyttsx3: {e}")

# --- Função para Interagir com Gemini (Corrigida e Refatorada) ---
def perguntaAoGemini(comando_do_usuario, nome_usuario="Cliente"):
    """
    Envia uma pergunta/comando para o modelo Gemini e retorna a resposta em texto.
    """
    try:
        # ATENÇÃO: Sua API Key. Para produção, use variáveis de ambiente.
        genai.configure(api_key="AIzaSyCAZ9rkZnmDO7KZRWss8_AWsQ9zdlTkUVY") # Substitua pela sua API Key

        # Concatena a persona com a pergunta atual do usuário
        prompt_completo = (
            f"{PROMPT_PERSONA}"
            f"O cliente '{nome_usuario}' disse/perguntou o seguinte: '{comando_do_usuario}'. "
            f"Responda apropriadamente ao que foi dito/perguntado. Se for uma saudação inicial como 'Olá', apresente-se brevemente, se não for uma saudação não cumprimente, vá direto ao ponto e responda."
        )
        
        print(f"[PROMPT ENVIADO AO GEMINI]: {prompt_completo}")

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_completo)
        
        texto_resposta = response.text
        print(f"[RESPOSTA GEMINI NO SERVIDOR]: {texto_resposta}")
        
        return texto_resposta
    except Exception as e:
        print(f"Erro ao interagir com Gemini: {e}")
        return "Desculpe, ocorreu um problema com a IA ao tentar processar sua solicitação."

# --- Endpoint Flask para Interação (Corrigido) ---
@app.route('/interact', methods=['POST'])
def handle_interaction():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "reply": "Nenhum dado JSON recebido."}), 400

        command_from_web = data.get('command')
        user_name_from_web = data.get('user', 'Cliente')

        if not command_from_web:
            return jsonify({"status": "error", "reply": "Comando não pode ser vazio."}), 400

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Comando HTTP ('{command_from_web}') recebido de '{user_name_from_web}'")
            
        resposta_gemini = perguntaAoGemini(command_from_web, user_name_from_web) 
            
        return jsonify({"status": "success", "reply": resposta_gemini})

    except Exception as e:
        print(f"Erro crítico no endpoint /interact: {e}")
        return jsonify({"status": "error", "reply": "Ocorreu um erro interno no servidor ao lidar com a interação."}), 500

# --- Bloco Principal para Execução do Servidor Flask ---
if __name__ == '__main__':
    print("===================================================")
    print(" Servidor Flask para Fidati Assistant IA Iniciado ")
    print("===================================================")
    print("Escutando por requisições HTTP em: http://127.0.0.1:5000/interact")
    print("Atenção: A saída de voz (TTS) agora é responsabilidade do cliente (navegador).")
    app.run(debug=True, port=5000)