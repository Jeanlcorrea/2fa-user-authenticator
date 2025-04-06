# 🛡️ FastAPI 2FA Auth App

Este projeto é um MVP de autenticação com dois fatores (2FA) usando FastAPI no backend e React no frontend.

## 🚀 Funcionalidades

- Registro de usuários
- Login com autenticação por senha
- Suporte a 2FA com QR Code e TOTP (Google Authenticator, Authy, etc.)
- Geração de tokens JWT
- Integração com frontend React (build servida via FastAPI)


## 🧪 Como rodar localmente

1. Clone o projeto

```bash
git clone https://github.com/Jeanlcorrea/2fa-user-authenticator
cd 2fa-user-authenticator
```

2. Instale as dependências do backend

```bash
pip install -r requirements.txt
```

3. Instale e build o frontend (React com Vite)

```bash
cd frontend
npm install
npm run build
cd ..
```

4. Rode a aplicação

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8007 --reload
```

Acesse em: [http://localhost:8007](http://localhost:8007)

## 🧰 Tecnologias

- Python 3.12
- FastAPI
- SQLite + SQLAlchemy
- Passlib (bcrypt)
- PyOTP + QRCode
- React + Vite

## 📌 Observações

- O projeto está em modo MVP e usa banco local SQLite.
- Ideal para testes de autenticação com 2FA.

