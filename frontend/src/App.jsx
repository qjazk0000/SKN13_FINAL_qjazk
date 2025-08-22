import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login/Login";
import MyPage from "./pages/MyPage/MyPage";
import ChatPage from "./pages/Chat/ChatPage";
import MembersPage from "./pages/Admin/MembersPage";
import ChatReportsPage from "./pages/Admin/ChatReportsPage";
import ManageReceipts from "./pages/Admin/ManageReceipts";
import ErrorBoundary from "./components/ErrorBoundary";

import "./App.css";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/mypage" element={<MyPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/admin/members" element={<MembersPage />} />
        <Route path="/admin/chat-reports" element={<ChatReportsPage />} />
        <Route path="/admin/manage-receipts" element={<ManageReceipts />} />
      </Routes>
    </Router>
  );
}

export default App;
