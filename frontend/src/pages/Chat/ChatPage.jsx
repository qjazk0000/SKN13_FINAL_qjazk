// ChatPage.jsx
// todo: 실제 API 엔드포인트에 맞게 수정
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
  const [lockedChatId, setLockedChatId] = useState(null);

  const [selectedChatId, setSelectedChatId] = useState(() => {
    return sessionStorage.getItem("selectedChatId") || null;
  });
  const [selectedReceiptId, setSelectedReceiptId] = useState(() => {
    return sessionStorage.getItem("selectedReceiptId") || null;
  });
  const [selectedCategory, setSelectedCategory] = useState(() => {
    return sessionStorage.getItem("selectedCategory") || "업무 가이드";
  });

  const [receiptDetails, setReceiptDetails] = useState(null);

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

      if (currentUser && (currentUser.name || currentUser.username)) {
        setUserName(currentUser.name || currentUser.username);

        const adminStatus = authService.isAdmin();
        setIsAdmin(adminStatus);
      } else {
        alert("로그인이 필요합니다.");
        navigate("/login");
      }
    };

    loadUserInfo();
  }, [navigate]);

  // 초기 채팅 데이터 로드
  useEffect(() => {
    const fetchChatsAndReceipts = async () => {
      setIsSidebarLoading(true);
      try {
        const [chatResponse, receiptResponse] = await Promise.all([
          api.get("/chat/list/"),
          api.get("/receipt/list/"),
        ]);
        // 백엔드 응답 형태가 배열이 아닐 수도 있으므로 안전하게 파싱
        const chatsData = Array.isArray(chatResponse?.data)
          ? chatResponse.data
          : Array.isArray(chatResponse?.data?.results)
          ? chatResponse.data.results
          : Array.isArray(chatResponse?.data?.data)
          ? chatResponse.data.data
          : [];

        const receiptsData = Array.isArray(
          receiptResponse?.data?.data?.receipts
        )
          ? receiptResponse.data.data.receipts.map((r) => ({
              ...r,
              id: r.receipt_id,
              title: new Date(r.created_at).toLocaleDateString(),
            }))
          : [];

        // normalizeChat을 사용하여 안전한 스키마로 변환
        const normalizedChats = chatsData.map(normalizeChat);

        // DB에서 가져온 메시지에 isNew: false 플래그 추가
        // info: 여기서 isNew 필드를 수정하기 때문에 채팅 목록이 바뀔 때마다 메시지가 다시 스트리밍됨
        const chatsWithMessageFlags = normalizedChats.map((chat) => ({
          ...chat,
          messages: chat.messages.map((message) => ({
            ...message,
            isNew: false, // DB에서 가져온 메시지는 타이핑 효과 적용 안함
          })),
        }));

        setChats(chatsWithMessageFlags);
        setReceipts(receiptsData);

        // if (selectedCategory === "업무 가이드" && chatsData.length > 0) {
        //   setSelectedChatId(chatsData[0].id);
        // } else if (
        //   selectedCategory === "영수증 처리" &&
        //   receiptsData.length > 0
        // ) {
        //   setSelectedReceiptId(receiptsData[0].receipt_id);
        // }
      } catch (error) {
        console.error("데이터 로드 실패:", error);
        // 실패해도 UI는 동작 가능하게 빈 배열 유지
        setChats([]);
        setReceipts([]);
      } finally {
        setIsSidebarLoading(false);
      }
    };

    fetchChatsAndReceipts();
  }, [selectedCategory]);

  const handleNewChat = useCallback(() => {
    setSelectedChatId(null);
    setSelectedReceiptId(null);
    sessionStorage.removeItem("selectedChatId");
    sessionStorage.removeItem("selectedReceiptId");

    // 이미 새 채팅이 있으면 그걸 선택
    const existingNewChat = chats.find((c) => c.isNew);
    if (existingNewChat) {
      setSelectedChatId(existingNewChat.id);
      setSelectedCategory("업무 가이드");
      setLockedChatId(existingNewChat.id);
      return;
    }

    // 프론트에서 임의 id로 새 채팅 생성
    const newChat = {
      id: `new-${Date.now()}`,
      title: "새 채팅",
      messages: [],
      isNew: true, // 임시 채팅임을 표시
    };

    setChats((prev) => [newChat, ...prev]);
    setSelectedChatId(newChat.id);
    setSelectedCategory("업무 가이드");
    setLockedChatId(newChat.id);
  }, [chats]);

  // 새 영수증 생성 핸들러
  const handleNewReceipt = useCallback(() => {
    setSelectedChatId(null);
    setSelectedReceiptId(null);
    sessionStorage.removeItem("selectedChatId");
    sessionStorage.removeItem("selectedReceiptId");

    const existingNewReceipt = receipts.find((r) => r.isNew);
    if (existingNewReceipt) {
      setSelectedReceiptId(existingNewReceipt.id);
      setSelectedCategory("영수증 처리");
      setReceiptDetails(null);
      return;
    }

    const newReceipt = {
      id: `new-${Date.now()}`,
      title: "새 영수증",
      isNew: true,
    };

    setReceipts((prev) => [newReceipt, ...prev]);
    setSelectedReceiptId(newReceipt.id);
    setSelectedCategory("영수증 처리");
    setReceiptDetails(null);
  }, [receipts]);

  const handleReceiptSaveSuccess = useCallback(async () => {
    setIsSidebarLoading(true);
    try {
      const response = await api.get("/receipt/list/");
      const receiptsData = Array.isArray(response?.data?.data?.receipts)
        ? response.data.data.receipts.map((r) => ({
            ...r,
            id: r.receipt_id,
            title: new Date(r.created_at).toLocaleDateString(),
          }))
        : [];
      setReceipts(receiptsData);
      setSelectedReceiptId(null);
      setReceiptDetails(null);
    } catch (error) {
      alert("영수증 목록을 새로고침하는 데 실패했습니다.");
    } finally {
      setIsSidebarLoading(false);
    }
  }, []);

  // 마이페이지 이동 핸들러
  const handleUserNameClick = useCallback(() => {
    navigate("/mypage");
    sessionStorage.clear();
  }, [navigate]);

  // 관리자 페이지로 이동 핸들러
  const handleAdminPageClick = useCallback(() => {
    navigate("/admin/members");
    sessionStorage.clear();
  }, [navigate]);

  // 채팅 선택 핸들러
  const handleSelectChat = useCallback(
    async (chat) => {
      if (chat.id === selectedChatId || isLoading) return;
      setIsLoading(true);

      try {
        // 채팅 메시지는 이미 대화방에 포함되어 있으므로 바로 선택
        setSelectedChatId(chat.id);
        sessionStorage.setItem("selectedChatId", chat.id);
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

      setSelectedChatId(null);
      setSelectedReceiptId(receipt.id);
      sessionStorage.setItem("selectedReceiptId", receipt.id);
      setSelectedCategory("영수증 처리");

      if (receipt.isNew) {
        setReceiptDetails(null);
        return;
      }

      setIsLoading(true);

      try {
        const response = await api.get(`/receipt/${receipt.id}/`);
        if (response.data.success) {
          setReceiptDetails(response.data.data);
        } else {
          throw new Error(response.data.message);
        }
      } catch (error) {
        alert("영수증을 불러오는 데 실패했습니다.");
        setSelectedReceiptId(null);
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

      if (lockedChatId === selectedChat.id) {
        setLockedChatId(null);
      }

      try {
        // const response = await api.post(`/chat/${selectedChat.id}/query/`, {
        //   message: message,
        // });
        // const aiResponseText = response.data.response;
        // const aiMessageId = response.data.message_id;
        // const conversationTitle = response.data.conversation_title; // 백엔드에서 반환된 제목

        let chatIdToUse = selectedChat.id;

        // 임시 채팅이면 DB에 먼저 저장
        if (selectedChat.isNew) {
          const raw = localStorage.getItem("user");
          const user = raw ? JSON.parse(raw) : null;
          const userId = user?.user_id;

          // DB에 새 채팅 생성
          const createRes = await api.post("/chat/new/", {
            title: message.slice(0, 50),
            user_id: userId,
          });
          const newChatFromDB = normalizeChat(createRes.data.data);

          // 임시 채팅을 DB 채팅으로 교체
          setChats((prevChats) =>
            prevChats.map((chat) =>
              chat.id === selectedChat.id
                ? {
                    ...newChatFromDB,
                    messages: [userMessage, aiLoadingMessage],
                    isNew: false,
                  }
                : chat
            )
          );
          setSelectedChatId(newChatFromDB.id);
          setLockedChatId(newChatFromDB.id);

          chatIdToUse = newChatFromDB.id;
        }

        // DB id로 쿼리 요청
        const response = await api.post(`/chat/${chatIdToUse}/query/`, {
          message: message,
        });
        const aiResponseText = response.data.response;
        const aiMessageId = response.data.message_id;
        const conversationTitle = response.data.conversation_title;

        // 채팅 제목 업데이트 (첫 질문인 경우)
        if (conversationTitle) {
          setChats((prevChats) =>
            prevChats.map((chat) =>
              chat.id === selectedChat.id
                ? { ...chat, title: conversationTitle }
                : chat
            )
          );
        }

        // AI 답변 완료 시 isNew: true로 설정 (TypingEffect 활성화)
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
                              id: aiMessageId,
                              content: aiResponseText,
                              isLoading: false,
                              isNew: true, // TypingEffect 활성화
                            }
                          : msg
                      )
                    : [
                        {
                          ...aiLoadingMessage,
                          id: aiMessageId,
                          content: aiResponseText,
                          isLoading: false,
                          isNew: true, // TypingEffect 활성화
                        },
                      ],
                }
              : chat
          )
        );

        // TypingEffect 완료 후 isNew: false로 변경 (setTimeout 사용)
        setTimeout(() => {
          setChats((prevChats) =>
            prevChats.map((chat) =>
              chat.id === selectedChat.id
                ? {
                    ...chat,
                    messages: Array.isArray(chat.messages)
                      ? chat.messages.map((msg) =>
                          msg.id === aiMessageId
                            ? {
                                ...msg,
                                isNew: false, // TypingEffect 비활성화
                              }
                            : msg
                        )
                      : chat.messages,
                  }
                : chat
            )
          );
        }, 100); // 100ms 후 isNew: false로 변경
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
    [selectedChat, isLoading, lockedChatId]
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
      window.location.href = "/"; // 강제로 루트 페이지로 이동
    }
  }, []);

  // 카테고리 선택 핸들러 (업무 가이드, 영수증 처리)
  const handleSelectCategory = useCallback((category) => {
    setSelectedCategory(category);
    sessionStorage.setItem("selectedCategory", category);

    if (category === "업무 가이드") {
      // 업무 가이드로 전환 → 영수증 선택값 초기화
      setSelectedReceiptId(null);
      setSelectedChatId(null);
      sessionStorage.removeItem("selectedReceiptId");
      sessionStorage.removeItem("selectedChatId");
    } else {
      // 영수증 처리로 전환 → 채팅 선택값 초기화
      setSelectedChatId(null);
      setSelectedReceiptId(null);
      sessionStorage.removeItem("selectedReceiptId");
      sessionStorage.removeItem("selectedChatId");
    }
  }, []);

  // 채팅 삭제 핸들러 추가
  const handleDeleteChat = useCallback(
    async (deletedChatId) => {
      try {
        // 로컬 상태에서 삭제된 채팅 제거 (즉시 UI 업데이트)
        setChats((prevChats) =>
          prevChats.filter((chat) => chat.id !== deletedChatId)
        );

        // 현재 선택된 채팅이 삭제된 채팅이라면 선택 해제
        if (selectedChatId === deletedChatId) {
          setSelectedChatId(null);
        }

        // 백엔드에서 최신 대화기록 다시 조회
        const chatResponse = await api.get("/chat/list/");

        // 백엔드 응답 형태가 배열이 아닐 수도 있으므로 안전하게 파싱
        const chatsData = Array.isArray(chatResponse?.data)
          ? chatResponse.data
          : Array.isArray(chatResponse?.data?.results)
          ? chatResponse.data.results
          : Array.isArray(chatResponse?.data?.data)
          ? chatResponse.data.data
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

        // 최신 대화기록으로 상태 업데이트
        setChats(chatsWithMessageFlags);
      } catch (error) {
        console.error("ChatPage: 대화기록 재조회 중 오류 발생:", error);
        // 오류 발생 시 사용자에게 알림
        alert(
          "채팅이 삭제되었지만 대화기록을 새로고침하는 데 실패했습니다. 페이지를 새로고침해주세요."
        );
      }
      setLockedChatId((prev) => (prev === deletedChatId ? null : prev));
    },
    [selectedChatId]
  );

  const sidebarList = selectedCategory === "업무 가이드" ? chats : receipts;

  useEffect(() => {
    // ① 영수증 처리 화면이고, selectedReceiptId가 있으면 상세 정보 자동 조회
    if (selectedCategory === "영수증 처리" && selectedReceiptId) {
      // ② 현재 영수증 목록(receipts)에서 선택된 영수증 객체 찾기
      const receipt = receipts.find((r) => r.id === selectedReceiptId);

      // ③ 영수증이 있고, 새 영수증이 아니라면(기존 영수증이면)
      if (receipt && !receipt.isNew) {
        setIsLoading(true); // ④ 로딩 상태 true로 설정

        // ⑤ API로 해당 영수증의 상세 정보 요청
        api
          .get(`/receipt/${selectedReceiptId}/`)
          .then((response) => {
            // ⑥ 응답 성공이면 상세 정보 상태에 저장
            if (response.data.success) {
              setReceiptDetails(response.data.data);
            } else {
              setReceiptDetails(null); // 실패 시 상세 정보 초기화
            }
          })
          .catch(() => setReceiptDetails(null)) // ⑦ 에러 발생 시 상세 정보 초기화
          .finally(() => setIsLoading(false)); // ⑧ 로딩 상태 false로 변경
      } else if (receipt && receipt.isNew) {
        // ⑨ 새 영수증이면 상세 정보 없음으로 처리
        setReceiptDetails(null);
      }
    }
  }, [selectedCategory, selectedReceiptId, receipts]);

  return (
    <div className="flex w-full min-h-screen bg-gray-100">
      <Sidebar
        userName={userName}
        chats={sidebarList}
        receipts={receipts}
        onNewChat={handleNewChat}
        onNewReceipt={handleNewReceipt}
        onSelectChat={handleSelectChat}
        onSelectReceipt={handleSelectReceipt}
        onSelectCategory={handleSelectCategory}
        selectedCategory={selectedCategory}
        selectedChatId={selectedChatId}
        selectedReceiptId={selectedReceiptId}
        onLogout={handleLogout}
        onUserNameClick={handleUserNameClick}
        isLoading={isSidebarLoading}
        isAdmin={isAdmin}
        onAdminPageClick={handleAdminPageClick}
        onDeleteChat={handleDeleteChat}
        isNewChatLocked={Boolean(lockedChatId)}
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
            receiptDetails={receiptDetails}
            onSaveSuccess={handleReceiptSaveSuccess}
          />
        )}
      </div>
    </div>
  );
}

export default ChatPage;
