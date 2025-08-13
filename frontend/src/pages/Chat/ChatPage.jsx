// ChatPage.jsx
// todo: 실제 API 엔드포인트에 맞게 수정

import axios from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";
import Chat from "./Chat";
import Receipt from "./Receipt";
import Sidebar from "./Sidebar";

function ChatPage() {
  const [chats, setChats] = useState([
    // 채팅 데이터 예시
    // { id: 1, title: "채팅방 1", messages: [] },
    // { id: 2, title: "채팅방 2", messages: [] },
  ]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarLoading, setIsSidebarLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("업무 가이드");

  const selectedChat = useMemo(
    () => chats.find((chat) => chat.id === selectedChatId) || null,
    [chats, selectedChatId]
  );

  // 초기 채팅 데이터 로드
  useEffect(() => {
    const fetchChats = async () => {
      setIsSidebarLoading(true);
      try {
        const response = await axios.get("/api/chats");
        setChats(response.data);
        if (response.data.length > 0) {
          setSelectedChatId(response.data[0].id);
        }
      } catch (error) {
        console.error("채팅 데이터 로드 실패:", error);
      } finally {
        setIsSidebarLoading(false);
      }
    };

    fetchChats();
  }, []);

  // 새 채팅 생성 핸들러
  const handleNewChat = useCallback(async () => {
    setIsLoading(true);

    try {
      const response = await axios.post("/api/chats");
      const newChat = response.data;

      setChats((prevChats) => [newChat, ...prevChats]);
      setSelectedChatId(newChat.id);
    } catch (error) {
      console.error("새 채팅 생성 실패:", error);
      alert("새 채팅을 생성하는 데 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 채팅 선택 핸들러
  const handleSelectChat = useCallback(
    async (chat) => {
      if (chat.id === selectedChatId || isLoading) return;
      setIsLoading(true);

      try {
        const response = await axios.get(`/api/chats/${chat.id}`);
        const messages = response.data.messages;

        setChats((prevChats) =>
          prevChats.map((c) => (c.id === chat.id ? { ...c, messages } : c))
        );
        setSelectedChatId(chat.id);
      } catch (error) {
        console.error("채팅 선택 실패:", error);
        alert("채팅을 불러오는 데 실패했습니다.");
      } finally {
        setIsLoading(false);
      }
    },
    [selectedChatId, isLoading]
  );

  // 메시지 전송 핸들러
  const handleSendMessage = useCallback(
    async (message) => {
      if (!selectedChat || isLoading) return;
      setIsLoading(true);

      const userMessage = {
        id: Date.now(),
        sender: "user",
        text: message,
      };

      const aiLoadingMessage = {
        id: Date.now() + 1, // ID가 겹치지 않도록 +1
        sender: "assistant",
        text: "...",
        isLoading: true,
      };

      setChats((prevChats) => {
        return prevChats.map((chat) =>
          chat.id === selectedChat.id
            ? {
                ...chat,
                messages: [...chat.messages, userMessage, aiLoadingMessage],
              }
            : chat
        );
      });

      try {
        const response = await axios.post("/api/chat", {
          chatId: selectedChat.id,
          userMessage: message,
        });
        const aiResponseText = response.data.aiResponse;

        setChats((prevChats) =>
          prevChats.map((chat) =>
            chat.id === selectedChat.id
              ? {
                  ...chat,
                  messages: chat.messages.map((msg) =>
                    msg.id === aiLoadingMessage.id
                      ? { ...msg, text: aiResponseText, isLoading: false }
                      : msg
                  ),
                }
              : chat
          )
        );
      } catch (error) {
        console.error("메시지 전송 실패:", error);
        // 에러 메시지 처리
        setChats((prevChats) =>
          prevChats.map((chat) =>
            chat.id === selectedChat.id
              ? {
                  ...chat,
                  messages: chat.messages.map((msg) =>
                    msg.id === aiLoadingMessage.id
                      ? {
                          ...msg,
                          text: "죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.",
                          isLoading: false,
                        }
                      : msg
                  ),
                }
              : chat
          )
        );
      } finally {
        setIsLoading(false);
      }
    },
    [selectedChat, isLoading]
  );

  // 로그아웃 핸들러
  const handleLogout = useCallback(async () => {
    try {
      await axios.post("/api/logout");
      alert("로그아웃 되었습니다.");
      window.location.href = "/";
    } catch (error) {
      console.error("로그아웃 실패:", error);
      alert("로그아웃 중 오류가 발생했습니다.");
    }
  }, []);

  // 카테고리 선택 핸들러 (업무 가이드, 영수증 처리)
  const handleSelectCategory = useCallback((category) => {
    setSelectedCategory(category);
    setSelectedChatId(null);
  }, []);

  return (
    <div className="flex w-full min-h-screen bg-gray-100">
      <Sidebar
        userName="홍길동"
        chats={chats}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onSelectCategory={handleSelectCategory}
        selectedCategory={selectedCategory}
        onLogout={handleLogout}
        isLoading={isSidebarLoading}
      />
      <div className="flex-grow flex justify-center items-center">
        {selectedCategory === "채팅방" || selectedCategory === "업무 가이드" ? (
          <Chat
            chat={selectedChat}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            selectedCategory={selectedCategory}
          />
        ) : (
          <Receipt selectedCategory={selectedCategory} />
        )}
      </div>
    </div>
  );
}

export default ChatPage;
