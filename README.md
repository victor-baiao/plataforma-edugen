# Plataforma Educativa Generativa (EduGen)

Projeto acadêmico desenvolvido para a disciplina de **Projeto Transversal em Redes de Comunicação 2** do Departamento de Engenharia Elétrica da Universidade de Brasília (UnB).

A **EduGen** é uma plataforma de ensino multimodal que utiliza Inteligência Artificial Generativa para criar aulas personalizadas sob demanda. O sistema gera slides visuais, narração em áudio neural e quizzes interativos sobre qualquer tópico solicitado pelo usuário.

## Autores

- **Victor Baião Pires** (Gerente de Projeto / Developer)
- **Tiago Matos da Ponte** (Developer)

## Estrutura do Projeto

O projeto é dividido em dois componentes principais:

- **[`/backend`](./backend)**: O cérebro da aplicação. Uma API em Python (Flask) que orquestra o Google Gemini (geração de roteiro), Edge-TTS (síntese de voz neural) e Pollinations.ai (geração de imagens).
- **[`/frontend`](./frontend)**: A interface do usuário. Uma Single Page Application (SPA) moderna construída com React, TypeScript e Tailwind CSS.

## Como Rodar o Projeto Completo

Para executar a plataforma localmente, você precisará de dois terminais abertos simultaneamente:

### Passo 1: Iniciar o Backend (Terminal 1)

```bash
cd backend
# Siga as instruções detalhadas no README dentro da pasta backend
python app.py
```

### Passo 2: Iniciar o Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Após iniciar ambos, acesse a aplicação em: `http://localhost:5173`
