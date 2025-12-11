import os
import google.generativeai as genai
import json
import uuid
import time
from gtts import gTTS
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
except KeyError:
    print("ERRO CRÍTICO: GOOGLE_API_KEY não encontrada.")

def generate_audio(text, filename):
    if not text or len(text.strip()) == 0:
        return False

    try:
        # lang='pt' para português genérico
        tts = gTTS(text=text, lang='pt')
        save_path = os.path.join(STATIC_DIR, filename)
        tts.save(save_path)
        return True
    except Exception as e:
        print(f"Erro ao salvar áudio {filename}: {e}")
        return False

def build_prompt(topic: str, level: str) -> str:
    return f"""
    Você é um professor universitário experiente e didático, você vai apenas ensinar uma única pessoa, então não se refira no plural como por exemplo: "Olá turma... Vocês... etc.".
    Crie uma aula completa em formato de SLIDES sobre "{topic}" (Nível: {level}).

    REGRAS OBRIGATÓRIAS DE CONTEÚDO:
    1. Gere EXATAMENTE 6 slides de conteúdo.
    2. O 'text' de cada slide deve ser um roteiro explicativo de APROXIMADAMENTE 50 A 60 PALAVRAS. Deve ser fluído para ser lido em voz alta.
    3. Gere EXATAMENTE 10 perguntas de múltipla escolha para o quiz final.

    ESTRUTURA JSON OBRIGATÓRIA:
    {{
      "slides": [
        {{
          "id": 1,
          "title": "Título Criativo do Slide",
          "text": "Texto explicativo (50-60 palavras) para o narrador...",
          "imagePrompt": "Prompt visual detalhado em INGLÊS para gerar uma imagem..."
        }}
        ... (repita para os 6 slides)
      ],
      "quiz": [
        {{
          "questionId": 1,
          "questionText": "Pergunta desafiadora baseada na aula...",
          "options": ["Opção A", "Opção B", "Opção C", "Opção D"],
          "correctOptionIndex": 0
        }}
        ... (repita para as 10 perguntas)
      ]
    }}
    Responda APENAS o JSON válido. Sem markdown.
    """

def clean_json_response(raw_text: str) -> dict:
    try:
        if raw_text.startswith("```json"): raw_text = raw_text[7:]
        if raw_text.endswith("```"): raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        return {"error": "Erro ao gerar JSON", "raw": raw_text}

@app.route('/api/generate-learning', methods=['POST'])
def generate_learning_content():
    try:
        data = request.get_json()
        topic = data.get('topic')
        level = data.get('level')

        print(f"Gerando aula sobre: {topic}")

        # Gera o Roteiro (Texto + Quiz) com Gemini
        prompt = build_prompt(topic, level)
        response = model.generate_content(prompt)
        content_data = clean_json_response(response.text)
        
        if "error" in content_data:
            print("Erro no JSON da IA:", content_data)
            return jsonify(content_data), 500

        # Processa os Slides (Imagens + Áudios)
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:5000')

        # Itera sobre os slides gerados pela IA
        if 'slides' in content_data:
            for i, slide in enumerate(content_data['slides']):
                # Imagem (Pollinations)
                encoded_prompt = slide['imagePrompt'].replace(" ", "%20")
                seed = uuid.uuid4().int % 100
                slide['imageUrl'] = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&seed={seed}"
                
                # Áudio (gTTS)
                audio_filename = f"{uuid.uuid4()}.mp3"
                
                # Delay para evitar erro 429 (Too Many Requests) do Google
                if i > 0: 
                    time.sleep(2) 
                
                success = generate_audio(slide['text'], audio_filename)
                
                if success:
                    slide['audioUrl'] = f"{base_url}/static/{audio_filename}"
                else:
                    slide['audioUrl'] = "" # Frontend trata se estiver vazio
        
        return jsonify(content_data), 200

    except Exception as e:
        print(f"ERRO GERAL NO SERVIDOR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)