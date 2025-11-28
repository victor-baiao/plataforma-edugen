import os
import google.generativeai as genai
import json
import uuid
import requests
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

# Configuração da IA (Gemini)
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-pro-latest')
except KeyError:
    print("ERRO CRÍTICO: GOOGLE_API_KEY não encontrada.")

def generate_voice_elevenlabs(text, filename):
    api_key = os.environ.get("ELEVEN_API_KEY")
    if not api_key:
        raise Exception("Chave ElevenLabs não configurada")

    # ID da voz "Brian" (Narrador Profissional) - Você pode trocar se quiser
    voice_id = "nPczCjz82INmrbC4qGTr" 
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", # Modelo que fala Português bem
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Erro ElevenLabs: {response.text}")

    save_path = os.path.join(STATIC_DIR, filename)
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

# --- MOTOR DE ÁUDIO 2: GOOGLE TTS (Fallback/Estepe) ---
def generate_voice_gtts(text, filename):
    if not text or len(text.strip()) == 0:
        return
    tts = gTTS(text=text, lang='pt')
    save_path = os.path.join(STATIC_DIR, filename)
    tts.save(save_path)

# --- GERADOR MESTRE DE ÁUDIO ---
def generate_audio(text, filename):
    # Tenta ElevenLabs primeiro (Melhor qualidade)
    try:
        print("Tentando gerar áudio com ElevenLabs...")
        generate_voice_elevenlabs(text, filename)
        return # Sucesso!
    except Exception as e:
        print(f"ElevenLabs falhou ou sem chave ({e}). Usando Google TTS.")
    
    # Se falhar (ou sem chave), usa Google (Garantido)
    generate_voice_gtts(text, filename)


def build_prompt(topic: str, level: str) -> str:
    return f"""
    Você é um professor universitário. Crie uma aula em SLIDES sobre "{topic}" (Nível: {level}).
    Gere um JSON com slides didáticos e um quiz final.
    ESTRUTURA JSON OBRIGATÓRIA:
    {{
      "slides": [
        {{
          "id": 1,
          "title": "Título...",
          "text": "Texto explicativo curto (max 40 palavras) para ser lido.",
          "imagePrompt": "Prompt visual em inglês..."
        }}
      ],
      "quiz": [
        {{
          "questionId": 1,
          "questionText": "...",
          "options": ["A", "B", "C", "D"],
          "correctOptionIndex": 0
        }}
      ]
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

        # 1. Gera Texto
        prompt = build_prompt(topic, level)
        response = model.generate_content(prompt)
        content_data = clean_json_response(response.text)
        
        if "error" in content_data: return jsonify(content_data), 500

        # 2. Processa Slides
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://127.0.0.1:5000')

        for slide in content_data['slides']:
            # Imagem
            encoded_prompt = slide['imagePrompt'].replace(" ", "%20")
            seed = uuid.uuid4().int % 100
            slide['imageUrl'] = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&seed={seed}"
            
            # Áudio (Chama a função inteligente)
            audio_filename = f"{uuid.uuid4()}.mp3"
            try:
                generate_audio(slide['text'], audio_filename)
                slide['audioUrl'] = f"{base_url}/static/{audio_filename}"
            except Exception as e:
                print(f"Erro fatal ao gerar áudio: {e}")
                slide['audioUrl'] = ""

        return jsonify(content_data), 200

    except Exception as e:
        print(f"ERRO GERAL: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)