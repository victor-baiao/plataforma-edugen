import os
import google.generativeai as genai
import json
import uuid
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

# Configuração da IA
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-pro-latest')
except KeyError:
    print("ERRO CRÍTICO: GOOGLE_API_KEY não encontrada.")

def generate_audio(text, filename):
    if not text or len(text.strip()) == 0:
        return

    tts = gTTS(text=text, lang='pt')
    
    save_path = os.path.join(STATIC_DIR, filename)
    tts.save(save_path)

def build_prompt(topic: str, level: str) -> str:
    return f"""
    Você é um professor universitário. Crie uma aula em SLIDES sobre "{topic}" (Nível: {level}).
    Gere um JSON com slides didáticos e um quiz final.
    
    ESTRUTURA JSON OBRIGATÓRIA:
    {{
      "slides": [
        {{
          "id": 1,
          "title": "Título do Slide",
          "text": "Texto explicativo curto e direto (máx 40 palavras) para ser lido em voz alta.",
          "imagePrompt": "Prompt visual em inglês para gerar uma imagem..."
        }}
      ],
      "quiz": [
        {{
          "questionId": 1,
          "questionText": "Pergunta...",
          "options": ["A", "B", "C", "D"],
          "correctOptionIndex": 0
        }}
      ]
    }}
    Responda APENAS o JSON válido.
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

        # 1. Gera Roteiro (Gemini)
        prompt = build_prompt(topic, level)
        response = model.generate_content(prompt)
        content_data = clean_json_response(response.text)
        
        if "error" in content_data: return jsonify(content_data), 500

        # 2. Processa Mídia (Slides)
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:5000')

        for slide in content_data['slides']:
            # Imagem (Pollinations)
            encoded_prompt = slide['imagePrompt'].replace(" ", "%20")
            seed = uuid.uuid4().int % 100
            slide['imageUrl'] = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&seed={seed}"
            
            # Áudio (Google TTS)
            audio_filename = f"{uuid.uuid4()}.mp3"
            try:
                generate_audio(slide['text'], audio_filename)
                slide['audioUrl'] = f"{base_url}/static/{audio_filename}"
            except Exception as e:
                print(f"Erro ao gerar áudio: {e}")
                slide['audioUrl'] = "" # Segue sem áudio se falhar

        return jsonify(content_data), 200

    except Exception as e:
        print(f"ERRO GERAL: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)