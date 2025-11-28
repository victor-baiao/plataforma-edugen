import os
import google.generativeai as genai
import json
import uuid
import asyncio
import edge_tts
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

if not os.path.exists('static'):
    os.makedirs('static')

# Configuração da IA
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('models/gemini-pro-latest')
except KeyError:
    print("Erro: GOOGLE_API_KEY não encontrada.")
    exit()

# Função assíncrona para gerar voz neural
async def generate_neural_voice(text, filename):
    voice = "pt-BR-AntonioNeural" 
    # ADICIONADO: rate="+50%" para velocidade 1.5x
    communicate = edge_tts.Communicate(text, voice, rate="+50%")
    await communicate.save(os.path.join('static', filename))

def build_prompt(topic: str, level: str) -> str:
    return f"""
    Você é um professor universitário experiente. Crie uma aula em formato de SLIDES sobre "{topic}" (Nível: {level}).

    Sua tarefa é gerar um JSON contendo uma lista de slides didáticos e um quiz final.
    
    ESTRUTURA OBRIGATÓRIA DO JSON:
    {{
      "slides": [
        {{
          "id": 1,
          "title": "Título do Slide (Ex: Introdução ao Conceito)",
          "text": "Texto explicativo detalhado para este slide (aprox. 50-60 palavras). Este texto será lido pelo narrador.",
          "imagePrompt": "Prompt curto em INGLÊS para gerar uma imagem ilustrativa específica para este slide (ex: 'diagram of tcp ip layers, minimalist, blue background')"
        }},
        ... (Gere entre 4 a 6 slides para cobrir o tópico)
      ],
      "quiz": [
        {{
          "questionId": 1,
          "questionText": "Pergunta baseada no conteúdo dos slides...",
          "options": ["A", "B", "C", "D"],
          "correctOptionIndex": 0
        }},
        ... (Gere 10 perguntas)
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

        prompt = build_prompt(topic, level)
        response = model.generate_content(prompt)
        content_data = clean_json_response(response.text)
        
        if "error" in content_data: return jsonify(content_data), 500

        for slide in content_data['slides']:
            encoded_prompt = slide['imagePrompt'].replace(" ", "%20")
            seed = uuid.uuid4().int % 100
            slide['imageUrl'] = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&seed={seed}"
            
            audio_filename = f"{uuid.uuid4()}.mp3"
            asyncio.run(generate_neural_voice(slide['text'], audio_filename))
            slide['audioUrl'] = f"http://127.0.0.1:5000/static/{audio_filename}"

        return jsonify(content_data), 200

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)