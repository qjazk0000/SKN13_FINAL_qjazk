import {
  ArrowPathIcon,
  EllipsisVerticalIcon,
  PlusIcon,
} from "@heroicons/react/24/outline";
import { useEffect, useRef, useState } from "react";
import LoadingMask from "../../components/LoadingMask";
import api from "../../services/api";

function Sidebar({
  userName,
  chats,
  receipts,
  onNewChat,
  onNewReceipt,
  onSelectChat,
  onSelectReceipt,
  onLogout,
  onUserNameClick,
  isLoading,
  onSelectCategory,
  selectedCategory,
  selectedChatId,
  selectedReceiptId,
  onDeleteChat,
  isNewChatLocked,
  isAdmin,
  onAdminPageClick,
}) {
  const initials = userName?.[0] || "U";
  const displayName = userName || "사용자";

  const [openDeleteMenuId, setOpenDeleteMenuId] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const menuRef = useRef(null);
  const listRef = useRef(null);

  useEffect(() => {
    const handleOutsideClick = (event) => {
      // 메뉴가 열려있고, 클릭된 요소가 메뉴 내부에 있지 않으면 메뉴를 닫습니다.
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setOpenDeleteMenuId(null);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [menuRef]);

  const getCategoryClass = (categoryName) => {
    return selectedCategory === categoryName
      ? "bg-gray-700 text-white"
      : "text-gray-300 hover:bg-gray-700 hover:text-white";
  };

  const isChatCategory = selectedCategory === "업무 가이드";

  const handleAddNewItem = () => {
    if (isChatCategory) {
      onNewChat();
    } else {
      onNewReceipt();
    }
  };

  const handleToggleDeleteMenu = (chatId, e) => {
    e.stopPropagation();
    setOpenDeleteMenuId((prev) => (prev === chatId ? null : chatId));

    // 열리는 경우에만 스크롤 살짝 맞춤
    if (openDeleteMenuId !== chatId) {
      const li = e.currentTarget.closest("li");
      // 컨테이너가 있으면, li를 컨테이너 내에서 보이게
      if (li && listRef.current) {
        li.scrollIntoView({ block: "nearest" });
      }
    }
  };

  const handleDelete = async (chatId) => {
    // 이미 삭제 중인 채팅인지 확인
    if (isDeleting) {
      console.log(`채팅 ${chatId}는 이미 삭제 중입니다.`);
      return;
    }

    try {
      // 삭제 중 상태로 설정
      setIsDeleting(true);

      // API 호출하여 채팅 삭제
      const response = await api.delete(`/chat/${chatId}/delete/`);

      if (response.data.success) {
        // 부모 컴포넌트에 삭제 완료 알림
        if (onDeleteChat) {
          onDeleteChat(chatId);
        }

        // 삭제 메뉴 닫기
        setOpenDeleteMenuId(null);
      } else {
        console.error("채팅 삭제 실패:", response.data.message);
        alert("채팅 삭제에 실패했습니다: " + response.data.message);
      }
    } catch (error) {
      console.error("채팅 삭제 중 오류 발생:", error);

      // 이미 삭제된 채팅인지 확인
      if (error.response?.status === 404) {
        alert("이미 삭제된 채팅입니다.");
      } else {
        alert("채팅 삭제 중 오류가 발생했습니다.");
      }
    } finally {
      // 삭제 중 상태 해제
      setIsDeleting(false);
    }
  };

  return (
    <>
      {/* LoadingMask */}
      <LoadingMask isVisible={isDeleting} message="채팅을 삭제하는 중..." />

      <div className="flex flex-col w-72 h-screen bg-gray-800 text-white">
        {/* 상단 로고 */}
        <div
          className="flex items-center justify-center h-16 border-b border-gray-700 cursor-pointer"
          onClick={() => {
            sessionStorage.clear();
            window.location.reload();    
          }}
        >
          {/* <h1 className="text-xl font-bold">NAVI</h1> */}
          <img src="/images/logo3.png" alt="NAVI Logo" className="h-28 mr-3" />
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

        {/* 새 채팅 + 목록 */}
        <div className="px-2 py-4 border-t border-gray-700 flex-1 flex flex-col min-h-0">
          <button
            type="button"
            onClick={handleAddNewItem}
            className={`w-full mb-4 py-2 px-4 rounded-md text-left flex items-center gap-2 transition ${
              (isChatCategory && isNewChatLocked) || isLoading
                ? "bg-gray-500 cursor-not-allowed opacity-60"
                : "bg-gray-600 hover:bg-gray-500 text-white"
            }`}
            disabled={(isChatCategory && isNewChatLocked) || isLoading}
          >
            <span>
              <PlusIcon className="w-5 h-5" />
            </span>
            <span>{isChatCategory ? "새 채팅" : "새 영수증"}</span>
          </button>

          {isLoading ? (
            <div className="flex justify-center items-center h-full text-gray-400">
              <ArrowPathIcon className="h-6 w-6 animate-spin" />
            </div>
          ) : (
            <div ref={listRef} className="overflow-y-auto">
              <ul>
                {isChatCategory
                  ? chats.map((chat, index) => {
                      const isSelected = selectedChatId === chat.id;
                      const isLastItem = index === chats.length - 1;

                      return (
                        <li
                          key={chat.id}
                          className={`relative mr-1 ${
                            openDeleteMenuId === chat.id || isSelected
                              ? "bg-gray-700 rounded-md"
                              : ""
                          }`}
                        >
                          <button
                            type="button"
                            onClick={() => onSelectChat(chat)}
                            className="w-full text-left block px-4 py-2 text-gray-300 rounded-md hover:bg-gray-700 hover:text-white transition truncate"
                            title={chat.title}
                          >
                            {chat.title}
                          </button>

                          <div className="absolute top-0 right-0 h-full flex items-center">
                            <div
                              className="relative"
                              ref={
                                openDeleteMenuId === chat.id ? menuRef : null
                              }
                            >
                              <button
                                onClick={(e) => {
                                  handleToggleDeleteMenu(chat.id, e);
                                }}
                                className="px-2 text-gray-400 hover:text-white focus:outline-none"
                              >
                                <EllipsisVerticalIcon className="w-5 h-5" />
                              </button>

                              {/* 드롭다운 메뉴 (삭제 버튼) */}
                              {openDeleteMenuId === chat.id && (
                                <div
                                  className={`absolute ${
                                    isLastItem ? "bottom-8" : "mt-1"
                                  } right-2 z-10 bg-gray-600 hover:bg-gray-700 rounded-md shadow-lg min-w-16`}
                                >
                                  <button
                                    onClick={() => handleDelete(chat.id)}
                                    disabled={isDeleting}
                                    className={`w-full text-left px-4 py-2 text-sm text-white transition ${
                                      isDeleting
                                        ? "opacity-50 cursor-not-allowed"
                                        : "hover:bg-gray-700"
                                    }`}
                                  >
                                    {isDeleting ? "삭제 중..." : "삭제"}
                                  </button>
                                </div>
                              )}
                            </div>
                          </div>
                        </li>
                      );
                    })
                  : receipts.map((receipt, index) => {
                      const isSelected =
                        selectedReceiptId === receipt.receipt_id;
                      return (
                        <li
                          key={receipt.receipt_id || index}
                          className={`relative mr-1 ${
                            isSelected ? "bg-gray-700 rounded-md" : ""
                          }`}
                        >
                          <button
                            type="button"
                            onClick={() => onSelectReceipt(receipt)}
                            className="w-full text-left block px-4 py-2 text-gray-300 rounded-md hover:bg-gray-700 hover:text-white transition truncate"
                            title={receipt.created_at}
                          >
                            {receipt.created_at
                              ? new Date(receipt.created_at).toLocaleString(
                                  "ko-KR",
                                  {
                                    year: "numeric",
                                    month: "2-digit",
                                    day: "2-digit",
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  }
                                )
                              : "새 영수증"}
                          </button>
                        </li>
                      );
                    })}
              </ul>
            </div>
          )}
        </div>

        {/* 관리자 페이지 버튼 */}
        {isAdmin && (
          <div className="px-4 py-2 border-t border-gray-700">
            <button
              type="button"
              onClick={onAdminPageClick}
              className="w-full py-2 px-4 text-white text-center font-medium underline hover:text-gray-400 transition"
              title="관리자 페이지로 이동"
            >
              관리자 페이지
            </button>
          </div>
        )}

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
                  className="text-m font-bold truncate hover:text-gray-400 transition cursor-pointer"
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
    </>
  );
}

export default Sidebar;
