import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login/Login";
import ChatPage from "./pages/Chat/ChatPage";
import MembersPage from "./pages/Admin/MembersPage";
import ChatReportsPage from "./pages/Admin/ChatReportsPage";
import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/admin/members" element={<MembersPage />} />
        <Route path="/admin/chat-reports" element={<ChatReportsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
