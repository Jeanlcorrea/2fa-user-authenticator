# 🛡️ FastAPI 2FA Auth App

This project is an MVP for two-factor authentication (2FA) using FastAPI on the backend and React on the frontend.

## 🚀 Production Deployment

This app is currently deployed and available at:

🌐 **[Live App on Railway](https://fastapi-react-app-production.up.railway.app)**  


## 🚀 Features

- User registration
- Login with password authentication
- 2FA support with QR Code and TOTP (Google Authenticator, Authy, etc.)
- JWT token generation
- React frontend integration (build served via FastAPI)

## 🧪 How to run locally

1. Clone the project

```bash
git clone https://github.com/Jeanlcorrea/2fa-user-authenticator
cd 2fa-user-authenticator
```

2. Install backend dependencies

```bash
pip install -r requirements.txt
```

3. Install and build the frontend (React with Vite)

```bash
cd frontend
npm install
npm run build
cd ..
```

4. Run the application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
```

Access it at: [http://localhost:8007](http://localhost:8007)

## 🧰 Technologies

- Python 3.12
- FastAPI
- SQLite + SQLAlchemy
- Passlib (bcrypt)
- PyOTP + QRCode
- React + Vite

## 📌 Notes

- This project is in MVP mode and uses a local SQLite database.
- Ideal for testing 2FA authentication flows.
