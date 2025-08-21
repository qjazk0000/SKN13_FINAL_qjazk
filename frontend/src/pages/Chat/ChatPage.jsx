// ChatPage.jsx
// todo: 실제 API 엔드포인트에 맞게 수정
import axios from "axios";
import api from "../../services/api";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../../services/authService";
import Chat from "./Chat";
import Receipt from "./Receipt";
import Sidebar from "./Sidebar";

// 모든 chat 오브젝트를 안전 스키마로 강제
const normalizeChat = (c) => ({
  id: c?.id ?? c?.session_id ?? c?.conversation_id ?? crypto.randomUUID(),
  title: c?.title ?? "새 채팅",
  messages: Array.isArray(c?.messages) ? c.messages : [],
});

function ChatPage() {
  const navigate = useNavigate();

  const [chats, setChats] = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [userName, setUserName] = useState("");

  const [selectedChatId, setSelectedChatId] = useState(null);
  const [selectedReceiptId, setSelectedReceiptId] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState("업무 가이드");

  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarLoading, setIsSidebarLoading] = useState(false);

  const selectedChat = useMemo(() => {
    const chat = (chats ?? []).find((chat) => chat.id === selectedChatId);
    return chat ? normalizeChat(chat) : null;
  }, [chats, selectedChatId]);

  const selectedReceipt = useMemo(
    () =>
      (receipts ?? []).find((receipt) => receipt.id === selectedReceiptId) ||
      null,
    [receipts, selectedReceiptId]
  );

  // 사용자 정보 로드
  useEffect(() => {
    const loadUserInfo = () => {
      const currentUser = authService.getCurrentUser();

      if (currentUser && currentUser.name) {
        setUserName(currentUser.name);

        const adminStatus = authService.isAdmin();
        setIsAdmin(adminStatus);
      } else {
        console.log("사용자 정보가 없습니다.");
        alert("로그인이 필요합니다.");
        navigate("/login");
      }
    };

    loadUserInfo();
  }, [navigate]);

  // 초기 채팅 데이터 로드
  useEffect(() => {
    const fetchChats = async () => {
      setIsSidebarLoading(true);
      try {
        const [chatResponse, receiptResponse] = await Promise.all([
          api.get("/chat/list/"),
          api.get("/receipt/"),
        ]);
        // 백엔드 응답 형태가 배열이 아닐 수도 있으므로 안전하게 파싱
        const chatsData = Array.isArray(chatResponse?.data)
          ? chatResponse.data
          : Array.isArray(chatResponse?.data?.results)
          ? chatResponse.data.results
          : Array.isArray(chatResponse?.data?.data)
          ? chatResponse.data.data
          : [];

        const receiptsData = Array.isArray(receiptResponse?.data)
          ? receiptResponse.data
          : Array.isArray(receiptResponse?.data?.results)
          ? receiptResponse.data.results
          : [];

        // normalizeChat을 사용하여 안전한 스키마로 변환
        const normalizedChats = chatsData.map(normalizeChat);

        // DB에서 가져온 메시지에 isNew: false 플래그 추가
        const chatsWithMessageFlags = normalizedChats.map((chat) => ({
          ...chat,
          messages: chat.messages.map((message) => ({
            ...message,
            isNew: false, // DB에서 가져온 메시지는 타이핑 효과 적용 안함
          })),
        }));

        setChats(chatsWithMessageFlags);
        setReceipts(receiptsData);

        if (selectedCategory === "업무 가이드" && chatsData.length > 0) {
          setSelectedChatId(chatsData[0].id);
        } else if (
          selectedCategory === "영수증 처리" &&
          receiptsData.length > 0
        ) {
          setSelectedReceiptId(receiptsData[0].id);
        }
      } catch (error) {
        console.error("데이터 로드 실패:", error);
        // 실패해도 UI는 동작 가능하게 빈 배열 유지
        setChats([]);
        setReceipts([]);
      } finally {
        setIsSidebarLoading(false);
      }
    };

    fetchChats();
  }, [selectedCategory]);

  // 새 채팅 생성 핸들러
  const handleNewChat = useCallback(async () => {
    setIsLoading(true);

    try {
      // JWT 토큰에서 user_id를 직접 추출
      const token = localStorage.getItem("access_token");
      console.log("DEBUG: 저장된 토큰:", token ? "있음" : "없음");

      let userId;
      if (token) {
        try {
          // JWT 토큰 디코딩 (base64 디코딩)
          const payload = JSON.parse(atob(token.split(".")[1]));
          userId = payload.user_id;
          console.log("DEBUG: JWT 토큰에서 추출한 user_id:", userId);
        } catch (error) {
          console.error("JWT 토큰 디코딩 실패:", error);
          // fallback: localStorage에서 사용자 정보 가져오기
          const currentUser = authService.getCurrentUser();
          userId = currentUser?.id;
          console.log("DEBUG: localStorage에서 가져온 user_id:", userId);
        }
      } else {
        // 토큰이 없으면 localStorage에서 사용자 정보 가져오기
        const currentUser = authService.getCurrentUser();
        userId = currentUser?.id;
        console.log("DEBUG: localStorage에서 가져온 user_id:", userId);
      }

      if (!userId) {
        throw new Error("사용자 ID를 찾을 수 없습니다. 다시 로그인해주세요.");
      }

      console.log("DEBUG: 최종 사용할 user_id:", userId);

      const response = await api.post("/chat/new/", {
        title: "새로운 대화",
        user_id: userId,
      });

      // 디버깅을 위한 로그 추가
      console.log("DEBUG: 새 채팅 생성 응답:", response.data);
      console.log("DEBUG: response.data.data:", response.data.data);
      console.log("DEBUG: response.data.data.id:", response.data.data?.id);
      console.log("DEBUG: response.data type:", typeof response.data);

      const newChat = normalizeChat(response.data.data); // response.data.data 사용
      console.log("DEBUG: normalizeChat 결과:", newChat);
      console.log("DEBUG: newChat.id:", newChat.id);

      setChats((prevChats) => [newChat, ...prevChats]);
      setSelectedChatId(newChat.id);
      setSelectedCategory("업무 가이드");
    } catch (error) {
      console.error("새 채팅 생성 실패:", error);
      alert("새 채팅을 생성하는 데 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 사용자 이름 클릭 핸들러 (MyPage로 이동)
  const handleUserNameClick = useCallback(() => {
    navigate("/mypage");
  }, [navigate]);

  // 관리자 페이지로 이동 핸들러
  const handleAdminPageClick = useCallback(() => {
    navigate("/admin/members");
  }, [navigate]);

  // 채팅 선택 핸들러
  const handleSelectChat = useCallback(
    async (chat) => {
      if (chat.id === selectedChatId || isLoading) return;
      setIsLoading(true);

      try {
        console.log("DEBUG: 채팅 선택됨:", chat);
        console.log("DEBUG: 선택된 채팅의 메시지:", chat.messages);

        // 채팅 메시지는 이미 대화방에 포함되어 있으므로 바로 선택

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

  // 영수증 채팅 선택 핸들러 (주석처리)
  const handleSelectReceipt = useCallback(
    async (receipt) => {
      if (receipt.id === selectedReceiptId || isLoading) return;
      setIsLoading(true);

      try {
        // 영수증 선택 시 바로 선택 (상세 데이터는 필요시 로드)
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
        sender_type: "user",
        content: message,
      };

      const aiLoadingMessage = {
        id: Date.now() + 1, // ID가 겹치지 않도록 +1
        sender_type: "ai",
        content: "...",
        isLoading: true,
      };

      setChats((prevChats) =>
        prevChats.map((chat) =>
          chat.id === selectedChat.id
            ? {
                ...chat,
                messages: Array.isArray(chat.messages)
                  ? [...chat.messages, userMessage, aiLoadingMessage]
                  : [userMessage, aiLoadingMessage],
              }
            : chat
        )
      );

      try {
        const response = await api.post(`/chat/${selectedChat.id}/query/`, {
          message: message,
        });
        const aiResponseText = response.data.response;

        setChats((prevChats) =>
          prevChats.map((chat) =>
            chat.id === selectedChat.id
              ? {
                  ...chat,
                  messages: Array.isArray(chat.messages)
                    ? chat.messages.map((msg) =>
                        msg.id === aiLoadingMessage.id
                          ? {
                              ...msg,
                              content: aiResponseText,
                              isLoading: false,
                              isNew: true,
                            }
                          : msg
                      )
                    : [
                        {
                          ...aiLoadingMessage,
                          content: aiResponseText,
                          isLoading: false,
                          isNew: true,
                        },
                      ],
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
                  messages: Array.isArray(chat.messages)
                    ? chat.messages.map((msg) =>
                        msg.id === aiLoadingMessage.id
                          ? {
                              ...msg,
                              content:
                                "죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.",
                              isLoading: false,
                              isNew: true,
                            }
                          : msg
                      )
                    : [
                        {
                          ...aiLoadingMessage,
                          content:
                            "죄송합니다. 메시지를 처리하는 중 오류가 발생했습니다.",
                          isLoading: false,
                          isNew: true,
                        },
                      ],
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
      console.error("백엔드 로그아웃 실패:", error);
      // 백엔드 실패해도 계속 진행
    } finally {
      // 성공/실패와 관계없이 로컬 로그아웃 처리
      localStorage.clear();

      // 명시적으로 루트 페이지로만 이동 (로그인 화면)
      console.log("로그아웃 완료, 루트 페이지(/)로 이동");
      window.location.href = "/"; // 강제로 루트 페이지로 이동
    }
  }, []);

  // 카테고리 선택 핸들러 (업무 가이드, 영수증 처리)
  const handleSelectCategory = useCallback((category) => {
    setSelectedCategory(category);
    setSelectedChatId(null);
  }, []);

  const sidebarList = selectedCategory === "업무 가이드" ? chats : receipts;

  // 초기 렌더 가드
  // if (isSidebarLoading) return <div className="p-4">불러오는 중…</div>;

  return (
    <div className="flex w-full min-h-screen bg-gray-100">
      <Sidebar
        userName={userName}
        chats={chats}
        onNewChat={handleNewChat}
        onNewReceipt={handleNewChat}
        onSelectChat={handleSelectChat}
        onSelectReceipt={handleSelectReceipt}
        onSelectCategory={handleSelectCategory}
        selectedCategory={selectedCategory}
        onLogout={handleLogout}
        onUserNameClick={handleUserNameClick}
        isLoading={isSidebarLoading}
        isAdmin={isAdmin}
        onAdminPageClick={handleAdminPageClick}
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
          <Receipt
            selectedCategory={selectedCategory}
            selectedReceipt={selectedReceipt}
          />
        )}
      </div>
    </div>
  );
}

export default ChatPage;
