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
    model = genai.GenerativeModel('models/gemini-pro-latest')
except KeyError:
    print("ERRO CRÍTICO: GOOGLE_API_KEY não encontrada.")

def generate_audio(text, filename):
    if not text or len(text.strip()) == 0:
        return

    try:
        tts = gTTS(text=text, lang='pt')
        save_path = os.path.join(STATIC_DIR, filename)
        tts.save(save_path)
        return True
    except Exception as e:
        print(f"Erro no gTTS para {filename}: {e}")
        return False

def build_prompt(topic: str, level: str) -> str:
    return f"""
    Você é um professor universitário experiente. Crie uma aula em SLIDES sobre "{topic}" (Nível: {level}).
    Gere um JSON com slides didáticos e um quiz final.
    
    REGRAS:
    1. Gere EXATAMENTE 6 slides.
    2. Texto explicativo de aprox 80 palavras por slide.
    3. Gere EXATAMENTE 10 perguntas no quiz.

    ESTRUTURA JSON:
    {{
      "slides": [
        {{
          "id": 1,
          "title": "Título...",
          "text": "Texto para ser lido...",
          "imagePrompt": "Prompt visual em inglês..."
        }}
      ],
      "quiz": [ ... ]
    }}
    Responda APENAS o JSON.
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

        prompt = build_prompt(topic, level)
        response = model.generate_content(prompt)
        content_data = clean_json_response(response.text)
        
        if "error" in content_data: return jsonify(content_data), 500

        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:5000')

        for i, slide in enumerate(content_data['slides']):
            # Imagem
            encoded_prompt = slide['imagePrompt'].replace(" ", "%20")
            seed = uuid.uuid4().int % 100
            slide['imageUrl'] = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&seed={seed}"
            
            # Áudio
            audio_filename = f"{uuid.uuid4()}.mp3"
            
            if i > 0: 
                time.sleep(2) 
            
            success = generate_audio(slide['text'], audio_filename)
            
            if success:
                slide['audioUrl'] = f"{base_url}/static/{audio_filename}"
            else:
                slide['audioUrl'] = "" 

        return jsonify(content_data), 200

    except Exception as e:
        print(f"ERRO GERAL: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)