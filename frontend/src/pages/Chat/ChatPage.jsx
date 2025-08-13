// ChatPage.jsx

import { useCallback, useMemo, useState } from "react";
import Chat from "./Chat";
import Sidebar from "./Sidebar";

function ChatPage() {
  const [chats, setChats] = useState([
    // { id: 1, title: "채팅방 1", messages: [] },
  ]);
  const [selectedChatId, setSelectedChatId] = useState(chats[0]?.id || null);
  const selectedChat = useMemo(
    () => chats.find((chat) => chat.id === selectedChatId) || null,
    [chats, selectedChatId]
  );

  // 새 채팅 생성 핸들러
  const handleNewChat = useCallback(() => {
    const maxId = chats.length > 0 ? Math.max(...chats.map((c) => c.id)) : 0;
    const newId = maxId + 1;
    const newChat = { id: newId, title: `채팅방 ${newId}`, messages: [] };

    setChats((prev) => [newChat, ...prev]);
    setSelectedChatId(newId);
  }, [chats]);

  // 채팅 선택 핸들러
  const handleSelectChat = useCallback((chat) => {
    setSelectedChatId(chat.id);
  }, []);

  const handleSendMessage = useCallback(
    (message) => {
      if (!selectedChat) return;

      const userMessage = {
        id: Date.now(),
        sender: "user",
        text: message,
      };

      // 중간 발표 시연용 코드임
      const messageCount = selectedChat.messages.length;
      let aiResponseText = "";

      if (messageCount === 0) {
        // 첫 번째 질문
        aiResponseText = `전산팀 주요 업무는 다음과 같습니다:

**전산팀 주요 업무**:
   - 원내 정보보안 및 개인정보보호 업무 총괄
   - 원내 정보보안 활동(보안성 검토, 용역 관리, 보안 적합성, 취약점 진단, 교육 등)

이러한 업무들은 전산팀의 전형적인 역할과 관련이 있으며, 정보 시스템 관리 및 보안, 데이터 관리 등이 포함됩니다.`;
      } else if (messageCount === 2) {
        // 두 번째 질문
        aiResponseText = `네, 근무 규정상 재택근무는 허용됩니다. 문서에 따르면, 원격근무제의 일환으로 재택근무형이 포함되어 있으며, 주 1일 또는 주 2일의 원격근무가 가능합니다. 원격근무를 신청할 경우 "원격근무근무계획서"와 "보안서약서"를 첨부해야 하며, 스마트워크근무형의 경우 추가적인 증빙자료가 필요할 수 있습니다.`;
      } else {
        // 그 외의 경우 (추가 질문 등)
        aiResponseText = "더 이상 준비된 응답이 없습니다.";
      }

      const aiMessage = {
        id: Date.now() + 1, // ID가 겹치지 않도록 +1
        sender: "assistant",
        // text: "네, 질문에 대한 답변입니다. 확인을 위해 임의로 작성되었습니다.",
        text: aiResponseText,
      };

      setChats((prevChats) =>
        prevChats.map((chat) =>
          chat.id === selectedChat.id
            ? { ...chat, messages: [...chat.messages, userMessage, aiMessage] }
            : chat
        )
      );
      console.log("메시지 전송:", message);
      console.log(chats);
    },
    [selectedChatId, chats]
  );

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
        <Chat chat={selectedChat} onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
}

export default ChatPage;
