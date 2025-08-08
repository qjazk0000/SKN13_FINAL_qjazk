import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login/Login";
import MyPage from "./pages/MyPage/MyPage";
import Chat from "./pages/Chat/Chat";
import PasswordChange from "./pages/PasswordChange/PasswordChange";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/mypage" element={<MyPage />} />
        <Route path="/change-password" element={<PasswordChange />} />
      </Routes>
    </Router>
  );
}

export default App;
