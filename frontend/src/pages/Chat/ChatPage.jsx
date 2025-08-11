// ChatPage.jsx

import { useCallback, useState, useMemo } from "react";
import Sidebar from "./Sidebar";
import Chat from "./Chat";

function ChatPage() {
  const [chats, setChats] = useState([{ id: 1, title: "채팅방 1" }]);
  const [selectedChatId, setSelectedChatId] = useState(chats[0]?.id || null);
  const selectedChat = useMemo(
    () => chats.find((chat) => chat.id === selectedChatId) || null,
    [chats, selectedChatId]
  );

  // 새 채팅 생성 핸들러
  const handleNewChat = useCallback(() => {
    const maxId = chats.length > 0 ? Math.max(...chats.map((c) => c.id)) : 0;
    const newId = maxId + 1;
    const newChat = { id: newId, title: `채팅방 ${newId}` };

    setChats((prev) => [newChat, ...prev]);
    setSelectedChatId(newId);
  }, [chats]);

  // 채팅 선택 핸들러
  const handleSelectChat = useCallback((chat) => {
    setSelectedChatId(chat.ChatId);
  }, []);

  // 로그아웃 핸들러
  const handleLogout = useCallback(() => {
    // TODO: 실제 로그아웃 로직으로 교체
    alert("로그아웃 되었습니다.");
    window.location.href = "/";
  }, []);

  return (
    <div className="flex w-full min-h-screen bg-gray-100">
      <Sidebar
        userName="홍길동"
        chats={chats}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onLogout={handleLogout}
      />
      <div className="flex-grow flex justify-center items-center">
        <Chat chat={selectedChat} />
      </div>
    </div>
  );
}

export default ChatPage;
