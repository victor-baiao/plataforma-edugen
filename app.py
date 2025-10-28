import os
import google.generativeai as genai
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Carregar variáveis de ambiente (ex: GOOGLE_API_KEY)
load_dotenv()

# Configurar a Flask App
app = Flask(__name__)

# Configurar a API do Gemini
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-pro-latest')
except KeyError:
    print("Erro: GOOGLE_API_KEY não encontrada. Defina-a no arquivo .env")
    exit()

def build_prompt(topic: str, level: str) -> str:
    """
    Constrói o prompt otimizado para a IA com base na entrada do usuário.
    """
    # A lógica de prompt detalhada, como mostrado na Seção 2.
    prompt_template = f"""
    Você é um especialista em pedagogia e engenharia de redes, atuando como um tutor generativo.
    Seu objetivo é gerar um material de aprendizado multimodal com base no input do usuário.

    Input do Usuário:
    - Tópico: "{topic}"
    - Nível: "{level}"

    Sua tarefa é gerar DUAS saídas em paralelo:

    1.  **Resumo do Vídeo (videoSummary):**
        - Gere um resumo textual detalhado (aprox. 150-200 palavras) que servirá como roteiro para um vídeo explicativo.
        - O conteúdo deve ser tecnicamente preciso e adequado ao nível "{level}".

    2.  **Quiz (quiz):**
        - Gere exatamente 10 perguntas de múltipla escolha baseadas EXCLUSIVAMENTE no conteúdo do "Resumo do Vídeo" que você acabou de criar.

    REQUISITO OBRIGATÓRIO DE FORMATO:
    Responda usando APENAS um bloco de código JSON válido.
    O formato JSON deve ser:
    {{
      "videoSummary": "Seu resumo textual aqui...",
      "quiz": [
        {{
          "questionId": 1,
          "questionText": "Sua pergunta 1 aqui...",
          "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
          "correctOptionIndex": 0
        }}
      ]
    }}
    """
    return prompt_template

def clean_json_response(raw_text: str) -> dict:
    """
    Limpa a resposta da IA, removendo marcadores de markdown (```json)
    para garantir que seja um JSON válido.
    """
    try:
        # Remove ```json e ``` do início e fim
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        
        return json.loads(raw_text.strip())
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return {"error": "Falha ao processar a resposta da IA", "raw": raw_text}


@app.route('/api/generate-learning', methods=['POST'])
def generate_learning_content():
    """
    Endpoint principal da API para o MVP.
    Recebe o tópico e o nível, e retorna o conteúdo gerado.
    """
    try:
        data = request.get_json()
        topic = data.get('topic')
        level = data.get('level')

        if not topic or not level:
            return jsonify({"error": "Tópico (topic) e nível (level) são obrigatórios"}), 400

        # 1. Construir o prompt otimizado
        optimized_prompt = build_prompt(topic, level)

        # 2. Executar a chamada à API de IA
        response = model.generate_content(optimized_prompt)

        # 3. Limpar e estruturar a resposta
        # A API do Gemini retorna o JSON como texto dentro de 'response.text'
        clean_data = clean_json_response(response.text)
        
        if "error" in clean_data:
             return jsonify(clean_data), 500

        # 4. Retornar o JSON limpo para o Frontend
        return jsonify(clean_data), 200

    except Exception as e:
        print(f"Erro inesperado no servidor: {e}")
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500

if __name__ == '__main__':
    # Para rodar localmente para testes: python app.py
    app.run(debug=True, port=5000)