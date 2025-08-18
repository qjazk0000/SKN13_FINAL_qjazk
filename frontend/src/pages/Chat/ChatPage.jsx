// ChatPage.jsx
// todo: 실제 API 엔드포인트에 맞게 수정

import axios from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../../services/authService";
import Chat from "./Chat";
import Receipt from "./Receipt";
import Sidebar from "./Sidebar";

function ChatPage() {
  const navigate = useNavigate();
  const [chats, setChats] = useState([
    // 채팅 데이터 예시
    // { id: 1, title: "채팅방 1", messages: [] },
    // { id: 2, title: "채팅방 2", messages: [] },
  ]);
  const [receipts, setReceipts] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [selectedReceiptId, setSelectedReceiptId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarLoading, setIsSidebarLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("업무 가이드");
  const [userName, setUserName] = useState("");

  const selectedChat = useMemo(
    () => chats.find((chat) => chat.id === selectedChatId) || null,
    [chats, selectedChatId]
  );
  const selectedReceipt = useMemo(
    () => receipts.find((receipt) => receipt.id === selectedReceiptId) || null,
    [receipts, selectedReceiptId]
  );

  // 사용자 정보 로드
  useEffect(() => {
    const loadUserInfo = () => {
      const currentUser = authService.getCurrentUser();
      if (currentUser && currentUser.name) {
        setUserName(currentUser.name);
      } else {
        // 사용자 정보가 없으면 루트 페이지로 이동
        // navigate('/');
        setUserName("사용자"); // 기본 사용자 이름 설정
      }
    };

    loadUserInfo();
  }, [navigate]);

  // 초기 데이터 로드
  useEffect(() => {
    const fetchData = async () => {
      setIsSidebarLoading(true);
      try {
        const [chatResponse, receiptResponse] = await Promise.all([
          axios.get("/api/chats"),
          axios.get("/api/receipts"), // 영수증 목록 API 호출
        ]);

        setChats(chatResponse.data);
        setReceipts(receiptResponse.data);

        if (
          selectedCategory === "업무 가이드" &&
          chatResponse.data.length > 0
        ) {
          setSelectedChatId(chatResponse.data[0].id);
        } else if (
          selectedCategory === "영수증 처리" &&
          receiptResponse.data.length > 0
        ) {
          setSelectedReceiptId(receiptResponse.data[0].id);
        }
      } catch (error) {
        console.error("데이터 로드 실패:", error);
      } finally {
        setIsSidebarLoading(false);
      }
    };

    fetchData();
  }, [selectedCategory]);

  // 새 채팅 생성 핸들러
  const handleNewChat = useCallback(async () => {
    setIsLoading(true);

    try {
      // const response = await axios.post("/api/chats");
      // const newChat = response.data;
      // setChats((prevChats) => [newChat, ...prevChats]);
      // setSelectedChatId(newChat.id);

      // Mock API 응답 (실제 API 연동 시 제거 필요)
      const mockResponse = {
        data: {
          id: Date.now(), // 고유한 ID 생성
          title: "새 채팅",
          messages: [],
        },
      };
      await new Promise((resolve) => setTimeout(resolve, 500));
      const newChat = mockResponse.data;
      setChats((prevChats) => [newChat, ...prevChats]);
      setSelectedChatId(newChat.id);
    } catch (error) {
      console.error("새 채팅 생성 실패:", error);
      alert("새 채팅을 생성하는 데 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 새 영수증 채팅 생성 핸들러
  const handleNewReceipt = useCallback(async () => {
    setIsLoading(true);

    try {
      // const response = await axios.post("/api/receipts");
      // const newReceipt = response.data;

      // setReceipts((prevReceipts) => [newReceipt, ...prevReceipts]);
      // setSelectedReceiptId(newReceipt.id);
      // setSelectedCategory("영수증 처리");

      // Mock API 응답 (실제 API 연동 시 제거 필요)
      const mockResponse = {
        data: {
          id: Date.now(), // 고유한 ID 생성
          title: "새 영수증",
          data: {}, // 영수증 데이터 초기화
        },
      };
      await new Promise((resolve) => setTimeout(resolve, 500));
      const newReceipt = mockResponse.data;
      setReceipts((prevReceipts) => [newReceipt, ...prevReceipts]);
      setSelectedReceiptId(newReceipt.id);
      setSelectedCategory("영수증 처리");
    } catch (error) {
      console.error("새 영수증 생성 실패:", error);
      alert("새 영수증을 생성하는 데 실패했습니다.");
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
        const response = await axios.get(`/api/chats/${chat.id}/messages`);
        const messages = response.data;

        setChats((prevChats) =>
          prevChats.map((c) => (c.id === chat.id ? { ...c, messages } : c))
        );
        setSelectedChatId(chat.id);
        setSelectedCategory("업무 가이드");
      } catch (error) {
        console.error("채팅 선택 실패:", error);
        alert("채팅을 불러오는 데 실패했습니다.");
      } finally {
        setIsLoading(false);
      }
    },
    [selectedChatId, isLoading]
  );

  // 영수증 채팅 선택 핸들러
  const handleSelectReceipt = useCallback(
    async (receipt) => {
      if (receipt.id === selectedReceiptId || isLoading) return;
      setIsLoading(true);

      try {
        // todo: 영수증 상세 데이터 불러오기 API 연동
        const response = await axios.get(`/api/receipts/${receipt.id}`);
        const receiptData = response.data;
        // 영수증 상태 업데이트
        setReceipts((prevReceipts) =>
          prevReceipts.map((r) =>
            r.id === receipt.id ? { ...r, data: receiptData.data } : r
          )
        );
        setSelectedReceiptId(receipt.id);
        setSelectedCategory("영수증 처리");
      } catch (error) {
        console.error("영수증 선택 실패:", error);
        alert("영수증을 불러오는 데 실패했습니다.");
      } finally {
        setIsLoading(false);
      }
    },
    [selectedReceiptId, isLoading]
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
        prevChats.map((chat) =>
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
      // 백엔드에 로그아웃 요청 (토큰 무효화)
      const response = await authService.logout();

      // 백엔드 응답 확인
      if (response && response.success) {
        console.log("백엔드 로그아웃 성공:", response.message);
      }
    } catch (error) {
      alert("로그아웃 중 오류가 발생했습니다.");
      console.error("백엔드 로그아웃 실패:", error);
      // 백엔드 실패해도 계속 진행
    } finally {
      // 성공/실패와 관계없이 로컬 로그아웃 처리 (삭제 필요)
      localStorage.clear();
      window.location.href = "/";
    }
  }, []);

  // 카테고리 선택 핸들러 (업무 가이드, 영수증 처리)
  const handleSelectCategory = useCallback((category) => {
    setSelectedCategory(category);
    setSelectedChatId(null);
    setSelectedReceiptId(null);
  }, []);

  const sidebarList = selectedCategory === "업무 가이드" ? chats : receipts;

  return (
    <div className="flex w-full min-h-screen bg-gray-100">
      <Sidebar
        userName={userName}
        chats={sidebarList}
        onNewChat={handleNewChat}
        onNewReceipt={handleNewReceipt}
        onSelectChat={handleSelectChat}
        onSelectReceipt={handleSelectReceipt}
        onSelectCategory={handleSelectCategory}
        selectedCategory={selectedCategory}
        onLogout={handleLogout}
        isLoading={isSidebarLoading}
      />
      <div className="flex-grow flex justify-center items-center">
        {selectedCategory === "업무 가이드" ? (
          <Chat
            chat={selectedChat}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            selectedCategory={selectedCategory}
          />
        ) : (
          <Receipt
            selectedReceipt={selectedReceipt}
            selectedCategory={selectedCategory}
            isLoading={isLoading}
          />
        )}
      </div>
    </div>
  );
}

export default ChatPage;
