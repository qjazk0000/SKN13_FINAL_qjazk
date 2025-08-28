// Chat.jsx
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import { PaperAirplaneIcon } from "@heroicons/react/24/solid";
import { useEffect, useRef, useState } from "react";
import MarkdownRenderer from "./MarkdownRenderer";
import TypingEffect from "./TypingEffect";
import api from "../../services/api";
import axios from "axios";

function Chat({ chat, onSendMessage, isLoading = false }) {
  const [text, setText] = useState("");
  const messageEndRef = useRef(null);
  const sessionStartAtRef = useRef(Date.now());

  // chat이 undefined일 때도 안전하게 처리
  const safeMessages =
    chat && Array.isArray(chat.messages) ? chat.messages : [];

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
      e.preventDefault();
      handleSend();
    }
  };

  const handleReport = async (messageId) => {
    try {
      const response = await api.post(
        `/chat/${messageId}/report/`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      if (response.data.status === "success") {
        alert("신고가 접수되었습니다.");
      } else {
        alert("신고 처리에 실패했습니다.");
      }
    } catch (error) {
      alert("신고 중 오류가 발생했습니다.");
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
      {/* NAVI 로고 헤더*/}
      {safeMessages.length === 0 && (
        <div className="flex flex-col items-center justify-center py-6 border-b">
          <img
            src="/images/NAVI.png"
            alt="NAVI Logo"
            className="w-20 h-auto mb-2"
          />
          <div className="text-lg font-bold text-gray-700">
            업무 가이드 챗봇
          </div>
        </div>
      )}

      <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
        {safeMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <p className="mt-4">메시지를 입력하여 대화를 시작하세요.</p>
          </div>
        ) : (
          safeMessages.map((message) => {
            const shouldAnimate =
              message.sender_type === "ai" &&
              message.isNew === true &&
              // created_at(ISO string) 기준. 없으면 서버에서 넣어줘야 함.
              message.created_at &&
              new Date(message.created_at).getTime() >=
                sessionStartAtRef.current;

            return (
              <div
                key={message.id}
                className={`flex ${
                  message.sender_type === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`p-3 rounded-lg max-w-sm ${
                    message.sender_type === "user"
                      ? "bg-gray-200 text-gray-800"
                      : "bg-orange-200 text-gray-800"
                  } whitespace-pre-wrap`}
                >
                  {message.sender_type === "ai" ? (
                    message.isLoading ? (
                      <span className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></span>
                        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></span>
                        <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-300"></span>
                      </span>
                    ) : // 새로 생성된 메시지만 타이핑 효과 적용
                    shouldAnimate ? (
                      <TypingEffect
                        text={message.content}
                        interval={25}
                        render={(partial) => (
                          <MarkdownRenderer content={partial} />
                        )}
                      />
                    ) : (
                      // 기존 DB 데이터는 즉시 표시
                      <MarkdownRenderer content={message.content} />
                    )
                  ) : (
                    message.content
                  )}
                </div>
                {/* 신고하기 버튼 */}
                {message.sender_type === "ai" && !message.isLoading && (
                  <button
                    className="ml-2 self-end text-xs text-gray-500 underline"
                    onClick={() => {
                      handleReport(message.id);
                      alert(`메시지 ${message.id} 신고하기 눌림`);
                    }}
                  >
                    신고하기
                  </button>
                )}
              </div>
            );
          })
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
