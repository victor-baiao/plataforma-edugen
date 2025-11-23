import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carregar a chave de API do arquivo .env
load_dotenv()
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Erro: GOOGLE_API_KEY não encontrada no .env")
    exit()

print("--- Modelos disponíveis que suportam 'generateContent' ---")

# Itera por todos os modelos que sua chave pode ver
for model in genai.list_models():
    # Verifica se o modelo suporta o método que precisamos ('generateContent')
    if 'generateContent' in model.supported_generation_methods:
        # Imprime o nome exato do modelo
        print(f"Nome do modelo: {model.name}")

print("---------------------------------------------------------")
print("Copie um 'Nome do modelo' da lista acima (ex: 'models/gemini-pro') e cole em app.py")