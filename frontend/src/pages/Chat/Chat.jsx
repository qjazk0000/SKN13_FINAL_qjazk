// Chat.jsx
import { useState, useCallback } from "react";
import { PaperAirplaneIcon } from "@heroicons/react/24/solid";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";

function Chat({ chat }) {
  const [text, setText] = useState("");
  //   const [isFirstMessage, setIsFirstMessage] = useState(true);

  return (
    <div className="flex flex-col w-full justify-center items-center px-48">
      <div className="flex flex-col items-center">
        <img
          src="/images/NAVI.png"
          alt="NAVI Logo"
          className="w-24 h-auto mb-4"
        />
        <div className="text-xl font-bold text-gray-700">
          "업무 가이드 챗봇"
        </div>
      </div>
      <div className="relative flex w-full mt-4">
        <textarea
          rows="2"
          placeholder="메시지를 입력하세요..."
          className="w-full p-2 pr-12 border border-gray-300 focus:outline-none rounded-2xl resize-y"
          value={text}
          onChange={(e) => setText(e.target.value)}
          //   onKeyDown={handleKeyDown}
        />
        <button
          className="absolute right-2 bottom-2 p-2 bg-gray-200 text-black rounded-full"
          //   onClick={handleSendClick}
          disabled={text.trim() === ""}
        >
          <PaperAirplaneIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}

export default Chat;
