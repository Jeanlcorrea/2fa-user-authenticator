import React, { useState } from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const API_URL = import.meta.env.VITE_API_URL;

export default function AuthApp() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [registerUsername, setRegisterUsername] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [userId, setUserId] = useState(null);
  const [qrCode, setQrCode] = useState(null);
  const [token, setToken] = useState(null);

  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showRegisterFormModal, setShowRegisterFormModal] = useState(false);
  const [showPostRegisterOptions, setShowPostRegisterOptions] = useState(false);
  const [show2FAModal, setShow2FAModal] = useState(false);

  const attemptLogin = async () => {
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        if (data.requires_2fa) {
          setUserId(data.user_id);
          setQrCode(`${API_URL}/qr-code/${data.user_id}`);
          setShow2FAModal(true);
          toast.info("Autenticação em duas etapas necessária.");
        } else {
          setToken(data.access_token);
          toast.success("Login bem-sucedido!");
          setUsername("");
          setPassword("");
          setOtp("");
          setQrCode(null);
        }
      } else {
        if (data.detail === "Usuário não encontrado") {
          setShowRegisterModal(true);
        } else if (data.detail === "Credenciais inválidas") {
          toast.error("Usuário ou senha incorretos.");
        } else {
          toast.error(data.detail || "Erro no login.");
        }
      }
    } catch (err) {
      console.error("Erro ao tentar login:", err);
      toast.error("Erro de conexão.");
    }
  };

  const loginWith2FA = async () => {
    const response = await fetch(`${API_URL}/login/2fa`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, otp_code: otp }),
    });

    const data = await response.json();

    if (response.ok) {
      setToken(data.access_token);
      toast.success("Login com 2FA bem-sucedido!");
      setShow2FAModal(false);
      setUsername("");
      setPassword("");
      setOtp("");
      setQrCode(null);
    } else {
      toast.error("Código OTP inválido.");
    }
  };

  const handleShowRegisterForm = () => {
    setRegisterUsername(username);
    setRegisterPassword(password);
    setShowRegisterModal(false);
    setShowRegisterFormModal(true);
  };

  const register = async () => {
    const response = await fetch(`${API_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: registerUsername,
        password: registerPassword,
      }),
    });
    const data = await response.json();

    if (response.ok) {
      setUserId(data.id);
      toast.success("Registro bem-sucedido!");
      setShowRegisterFormModal(false);
      setShowPostRegisterOptions(true);
    } else {
      toast.error(data.detail || "Erro no registro.");
    }
  };

  const enable2FA = async (id) => {
    const response = await fetch(`${API_URL}/enable-2fa/${id}`, {
      method: "POST",
    });
    if (response.ok) {
      toast.success("2FA ativado! Escaneie o QR Code.");
      setQrCode(`${API_URL}/qr-code/${id}`);
      setShow2FAModal(true);
    } else {
      toast.error("Erro ao ativar o 2FA.");
    }
  };

  return (
    <div className="container">
      <ToastContainer position="top-right" autoClose={3000} />
      <h2>Login</h2>
      <input
        type="text"
        placeholder="Usuário"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="input-field"
      />
      <input
        type="password"
        placeholder="Senha"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="input-field"
      />
      <button onClick={attemptLogin} className="action-button">
        Entrar
      </button>

      {showRegisterModal && (
        <div className="modal">
          <div className="modal-content">
            <h3>Usuário não encontrado</h3>
            <p>Deseja se registrar com essas credenciais?</p>
            <button onClick={handleShowRegisterForm} className="action-button">
              Registrar
            </button>
            <button
              onClick={() => setShowRegisterModal(false)}
              className="close-button"
            >
              Fechar
            </button>
          </div>
        </div>
      )}

      {showRegisterFormModal && (
        <div className="modal">
          <div className="modal-content">
            <h3>Registrar novo usuário</h3>
            <input
              type="text"
              placeholder="Usuário"
              value={registerUsername}
              onChange={(e) => setRegisterUsername(e.target.value)}
              className="input-field"
            />
            <input
              type="password"
              placeholder="Senha"
              value={registerPassword}
              onChange={(e) => setRegisterPassword(e.target.value)}
              className="input-field"
            />
            <button onClick={register} className="action-button">
              Confirmar Registro
            </button>
            <button
              onClick={() => setShowRegisterFormModal(false)}
              className="close-button"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {showPostRegisterOptions && (
        <div className="modal">
          <div className="modal-content">
            <h3>Deseja ativar o 2FA agora?</h3>
            <button
              className="action-button"
              onClick={() => {
                enable2FA(userId);
                setShowPostRegisterOptions(false);
              }}
            >
              Ativar 2FA
            </button>
            <button
              className="action-button"
              onClick={() => {
                toast.success("Login concluído!");
                setToken("fake-token");
                setUsername("");
                setPassword("");
                setOtp("");
                setQrCode(null);
                setShowPostRegisterOptions(false);
              }}
            >
              Pular etapa
            </button>
          </div>
        </div>
      )}

      {show2FAModal && (
        <div className="modal">
          <div className="modal-content">
            <h3>Autenticação de 2 Fatores</h3>
            {qrCode && (
              <div className="qr-container">
                <h4>Escaneie o QR Code</h4>
                <img src={qrCode} alt="QR Code" />
              </div>
            )}
            <input
              type="text"
              placeholder="Código OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="input-field"
            />
            <button onClick={loginWith2FA} className="action-button">
              Confirmar Código
            </button>
            <button
              onClick={() => setShow2FAModal(false)}
              className="close-button"
            >
              Fechar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
