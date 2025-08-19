// Chat.jsx
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import { PaperAirplaneIcon } from "@heroicons/react/24/solid";
import { useEffect, useRef, useState } from "react";
import TypingEffect from "./TypingEffect";

function Chat({ chat, onSendMessage, isLoading }) {
  const [text, setText] = useState("");
  const messageEndRef = useRef(null);

  // 메시지 전송 후 스크롤을 맨 아래로 이동
  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chat?.messages]);

  const handleSend = () => {
    if (text.trim() === "") return;
    onSendMessage(text);
    setText("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Enter 키를 눌렀을 때 줄바꿈 방지
      handleSend();
    }
  };

  if (!chat) {
    return (
      <div className="flex flex-col items-center justify-center text-gray-500">
        <img
          src="/images/NAVI.png"
          alt="NAVI Logo"
          className="w-24 h-auto mb-4"
        />
        <div className="text-xl font-bold text-gray-700">업무 가이드 챗봇</div>
        <p className="mt-4">채팅을 선택하거나 새 채팅을 시작하세요.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full h-[100dvh] sm:px-8 md:px-16 lg:px-32 xl:px-60 rounded-lg">
      <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
        {chat.messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <img
              src="/images/NAVI.png"
              alt="NAVI Logo"
              className="w-24 h-auto mb-4"
            />
            <div className="text-xl font-bold text-gray-700">
              업무 가이드 챗봇
            </div>
            <p className="mt-4">메시지를 입력하여 대화를 시작하세요.</p>
          </div>
        ) : (
          chat.messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`p-3 rounded-lg max-w-sm ${
                  message.sender === "user"
                    ? "bg-gray-200 text-gray-800"
                    : "bg-orange-200 text-gray-800"
                } whitespace-pre-wrap`}
              >
                {message.sender === "assistant" ? (
                  message.isLoading ? (
                    <span className="flex items-center space-x-2">
                      <span>답변 생성 중...</span>
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></span>
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></span>
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-300"></span>
                    </span>
                  ) : (
                    // 로딩 완료 시
                    <TypingEffect text={message.text} />
                  )
                ) : (
                  message.text
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messageEndRef} />
      </div>

      <div className="p-4 border-t flex items-start space-x-2 flex-shrink-0">
        <div className="relative flex-grow">
          <textarea
            rows="2"
            placeholder="메시지를 입력하세요..."
            className="w-full p-2 pr-14 border border-gray-300 focus:outline-none rounded-2xl resize-none"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            className="absolute right-2 top-4 bg-gray-400 text-white rounded-full p-2 h-10 w-10 flex items-center justify-center cursor-pointer transition-colors"
            onClick={handleSend}
            disabled={text.trim() === "" || isLoading}
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;
