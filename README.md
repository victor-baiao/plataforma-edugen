# Plataforma Educativa Generativa

Este repositório contém o código-fonte do **backend** para o projeto acadêmico "Plataforma EduGen". O projeto está sendo desenvolvido para a disciplina de **Projeto Transversal em Redes de Comunicação 2** do Departamento de Engenharia Elétrica da Universidade de Brasília (UnB).

Este serviço atua como o "núcleo" da plataforma. Sua responsabilidade é receber solicitações simples do frontend (um tópico e um nível de dificuldade), construir um prompt técnico otimizado e chamar a API de IA Generativa do Google (Gemini) para gerar um conteúdo de aprendizado completo e estruturado.

## Status Atual: Fase 2 Concluída

![Status](https://img.shields.io/badge/Status-Fase%202%20Conclu%C3%ADda-brightgreen)

Este código representa a conclusão bem-sucedida da **Fase 2: Integração do Core (Backend)**.

O marco principal atingido é a **Prova de Conceito (PoC) da Geração de Conteúdo**. O servidor é 100% capaz de receber uma requisição JSON, processá-la e retornar uma resposta JSON estruturada contendo:

- `videoSummary`: Um roteiro textual detalhado para um vídeo educativo sobre o tópico.
- `quiz`: Um array com 10 perguntas de múltipla escolha baseadas no resumo.

## Stack Tecnológica

- **Linguagem:** Python 3.10+
- **Framework de API:** Flask
- **IA Generativa:** Google Gemini (via biblioteca `google-generativeai`)
- **Modelo de IA:** `models/gemini-pro-latest`
- **Gerenciamento de Pacotes:** `pip` e `venv`
- **Gerenciamento de Segredos:** `python-dotenv`

---

## ⚙️ Instalação e Execução

Siga estes passos para configurar e executar o servidor backend localmente.

### 1. Pré-requisitos

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [Postman](https://www.postman.com/downloads/) (para testes nesta fase)

### 2. Clonar o Repositório

```bash
git clone [https://github.com/victor-baiao/plataforma-educativa-generativa.git](https://github.com/victor-baiao/plataforma-educativa-generativa.git)
cd plataforma-educativa-generativa
```

### 3. Configurar o Ambiente Virtual (Venv)

# Criar o ambiente virtual

python -m venv venv

# Ativar o ambiente (Windows)

.\venv\Scripts\activate

# Ativar o ambiente (macOS/Linux)

# source venv/bin/activate

### 4. Instalar as Dependências

pip install -r requirements.txt

### 5. Configurar a Chave de API (Obrigatório)

# 1- Crie um arquivo chamado .env na mesma pasta que o app.py

# 2- Abra o arquivo .env e adicione sua chave criada:

GOOGLE_API_KEY=SUA_CHAVE_DE_API_GERADA_NO_GOOGLE_AI_STUDIO

### 6. Verificar e configurar o modela de IA

# 1. Execute o script check_models.py:

python check_models.py

# 2. O terminal listará os modelos disponíveis para sua chave (ex: models/gemini-pro-latest).

# 3. Copie o nome de um modelo robusto da lista (ex: models/gemini-pro-latest).

# 4. Abra o arquivo app.py e cole esse nome na linha de configuração do modelo:

# - Verifique se esta linha corresponde a um modelo da sua lista

model = genai.GenerativeModel('models/gemini-pro-latest')

### 7. Executar o Servidor

python app.py

# O terminal deve exibir uma mensagem indicando que o servidor está rodando: \* Running on http://127.0.0.1:5000

### 8. Como Testar

# Nesta fase, o frontend (Fase 3) ainda não está conectado. Usamos o Postman para simular a requisição que o frontend fará.

# Instale e abra o Postman.

# Crie uma nova requisição com os seguintes parâmetros:

Método: POST

URL: http://127.0.0.1:5000/api/generate-learning

# Vá para a aba Body.

# Selecione a opção raw.

# Mude o tipo de Text para JSON.

# Cole o seguinte JSON no corpo (Body) da requisição:

JSON

{
"topic": "Princípio de funcionamento do TCP/IP",
"level": "Intermediário"
}

# Clique em Send.

# Pronto, deve retornar corretamente.
