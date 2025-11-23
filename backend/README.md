# EduGen - Backend

Este diretório contém a API RESTful da Plataforma EduGen. Ele atua como o motor de inteligência da aplicação, orquestrando múltiplos modelos de IA para gerar experiências de aprendizado multimodais.

## Funcionalidades

### 1. Geração de Roteiro Instrucional

Utiliza o **Google Gemini 1.5 Pro** para criar um plano de aula estruturado em slides didáticos, garantindo precisão técnica e adaptação ao nível de dificuldade solicitado (Iniciante, Intermediário, Avançado).

### 2. Síntese de Voz Neural (TTS)

Integração com a biblioteca **Edge-TTS** (baseada no Microsoft Azure Cognitive Services) para converter os textos dos slides em áudio natural.

- **Voz:** `pt-BR-AntonioNeural` (Voz masculina, formal e didática).
- **Velocidade:** Acelerada em **1.5x** (`rate="+50%"`) para uma dinâmica de aula mais ágil.

### 3. Ilustração Generativa

Geração de imagens sob demanda via **Pollinations.ai**. O backend solicita ao Gemini um "prompt visual" em inglês para cada slide e utiliza esse prompt para gerar ilustrações conceituais únicas e livres de direitos autorais.

### 4. Gamificação Automática

Geração de um **Quiz de Fixação** com 10 perguntas de múltipla escolha, incluindo gabarito e identificação da resposta correta, totalmente contextualizado com o conteúdo apresentado nos slides.

---

## Stack Tecnológica

- **Linguagem:** Python 3.10+
- **Framework Web:** Flask (com Flask-CORS para permitir requisições do React)
- **IA Generativa (Texto):** Google Generative AI SDK (`google-generativeai`)
- **IA Generativa (Áudio):** Edge TTS (`edge-tts`)
- **Gerenciamento de Assincronicidade:** `asyncio` (para geração de áudio paralela)
- **Utilitários:** `python-dotenv` (segurança), `uuid` (gestão de arquivos)

---

## Instalação e Configuração

Siga os passos abaixo para configurar o ambiente de desenvolvimento local.

### 1. Pré-requisitos

- Python 3.10 ou superior instalado.
- Uma chave de API válida do [Google AI Studio](https://aistudio.google.com/).

### 2. Configurar Ambiente Virtual (Recomendado)

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente (Windows)
.\venv\Scripts\activate

# Ativar o ambiente (Mac/Linux)
source venv/bin/activate
```

### 3. Instalar Dependências

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias usando o arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Caso tenha algum erro, tente adicionar manualmente as novas bibliotecas com:

```bash
pip install flask flask-cors python-dotenv google-generativeai edge-tts
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz desta pasta (`backend/`) e adicione sua chave de API. **Não compartilhe este arquivo.**

```bash
GOOGLE_API_KEY=sua_chave_secreta_aqui
```

### 5. Executar o Servidor

```bash
python app.py
```

O servidor iniciará em `http://127.0.0.1:5000`.
