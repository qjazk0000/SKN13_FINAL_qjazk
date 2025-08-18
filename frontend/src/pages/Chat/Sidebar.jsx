import { ArrowPathIcon, PlusIcon } from "@heroicons/react/24/solid";

function Sidebar({
  userName,
  chats,
  onNewChat,
  onSelectChat,
  onLogout,
  onUserNameClick,
  isLoading,
  onSelectCategory,
  selectedCategory,
}) {
  const initials = userName?.[0] || "U";
  const displayName = userName || "사용자";

  const getCategoryClass = (categoryName) => {
    return selectedCategory === categoryName
      ? "bg-gray-700 text-white"
      : "text-gray-300 hover:bg-gray-700 hover:text-white";
  };

  return (
    <div className="flex flex-col w-64 h-screen bg-gray-800 text-white">
      {/* 상단 로고 */}
      <div className="flex items-center justify-center h-16 border-b border-gray-700">
        <h1 className="text-xl font-bold">NAVI</h1>
      </div>

      {/* 카테고리 메뉴 */}
      <div className="flex flex-col px-2 py-4 gap-2">
        <div
          className={`flex items-center px-4 py-2 rounded-md cursor-pointer ${getCategoryClass(
            "업무 가이드"
          )}`}
          onClick={() => onSelectCategory("업무 가이드")}
        >
          업무 가이드
        </div>
        <div
          className={`flex items-center px-4 py-2 rounded-md cursor-pointer ${getCategoryClass(
            "영수증 처리"
          )}`}
          onClick={() => onSelectCategory("영수증 처리")}
        >
          영수증 처리
        </div>
      </div>

      {/* 새 채팅 + 채팅 리스트 */}
      <div className="p-4 border-t border-gray-700 flex-1 flex flex-col min-h-0">
        <button
          type="button"
          onClick={onNewChat}
          className="w-full mb-2 py-2 px-4 rounded-md bg-gray-600 hover:bg-gray-500 text-white text-left flex items-center gap-2 transition"
          disabled={isLoading}
        >
          <span>
            <PlusIcon className="w-5 h-5" />
          </span>
          새 채팅
        </button>

        {isLoading ? (
          // 로딩 중일 때
          <div className="flex justify-center items-center h-full text-gray-400">
            <ArrowPathIcon className="h-6 w-6 animate-spin" />
          </div>
        ) : (
          // 로딩이 끝났을 때
          <ul className="flex flex-col gap-2 flex-1 overflow-y-auto">
            {chats.map((chat) => (
              <li key={chat.id}>
                <button
                  type="button"
                  onClick={() => onSelectChat?.(chat)}
                  className="w-full text-left block px-4 py-2 text-gray-300 rounded-md hover:bg-gray-700 hover:text-white transition truncate"
                  title={chat.title}
                >
                  {chat.title}
                </button>
              </li>
            ))}
            {chats.length === 0 && (
              <li className="px-2 py-2 text-sm text-gray-400">
                채팅 내역이 없습니다.
              </li>
            )}
          </ul>
        )}
      </div>

      {/* 하단 사용자명 + 로그아웃 */}
      <div className="mt-auto px-4 py-3 border-t border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 min-w-0">
            <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gray-700 text-sm font-semibold">
              {initials}
            </div>
            <div className="min-w-0">
              <button
                type="button"
                onClick={onUserNameClick}
                className="text-m font-bold truncate hover:text-blue-300 transition cursor-pointer"
                title="마이페이지로 이동"
              >
                {displayName}
              </button>
            </div>
          </div>

          {/* 로그아웃 버튼 (inline SVG 아이콘) */}
          <button
            type="button"
            onClick={onLogout}
            className="p-2 rounded-md hover:bg-gray-700 transition"
            aria-label="로그아웃"
            title="로그아웃"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M15 3h-6a2 2 0 0 0-2 2v4" />
              <path d="M7 15v4a2 2 0 0 0 2 2h6" />
              <path d="M10 12h9" />
              <path d="m18 15 3-3-3-3" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
