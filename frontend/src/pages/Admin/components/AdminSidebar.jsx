import React from "react";
import { Link } from "react-router-dom";


function AdminSidebar({ userName, onUserNameClick, onLogout, selectedTab, onTabSelect, onChatPageClick }) {
  const initials = userName?.[0] || "A";
  const displayName = userName || "관리자";

  // 현재 선택된 탭에 따른 스타일 클래스 반환
  const getTabClass = (tabName) => {
    return selectedTab === tabName
      ? "bg-gray-700 text-white"
      : "text-gray-300 hover:bg-gray-700 hover:text-white";
  };

  return (
    <div className="flex flex-col w-64 bg-gray-800 text-white min-h-screen">
      {/* 상단 관리자 메뉴 */}
      <div className="p-4">
        <h2 className="text-xl font-bold mb-6">관리자 메뉴</h2>
        <div className="space-y-4">
          <div
            className={`flex items-center px-4 py-2 rounded-md cursor-pointer transition ${getTabClass("members")}`}
            onClick={() => onTabSelect("members")}
          >
            회원 관리
          </div>
          <div
            className={`flex items-center px-4 py-2 rounded-md cursor-pointer transition ${getTabClass("chat-reports")}`}
            onClick={() => onTabSelect("chat-reports")}
          >
            채팅 신고 내역
          </div>
          <div
            className={`flex items-center px-4 py-2 rounded-md cursor-pointer transition ${getTabClass("manage-receipt")}`}
            onClick={() => onTabSelect("manage-receipt")}
          >
            영수증 관리
          </div>
        </div>
      </div>

      {/* 하단 사용자명 + 로그아웃 */}
      <div className="mt-auto">
        {/* 채팅 화면으로 이동 버튼 - 사용자 프로필 바로 위 */}
        <div className="px-4 py-2 border-t border-gray-700">
          <button
            type="button"
            onClick={onChatPageClick}
            className="w-full py-2 px-4 rounded-md bg-green-600 hover:bg-green-700 text-white text-center font-medium transition flex items-center justify-center gap-2"
            title="채팅 화면으로 이동"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            채팅 화면
          </button>
        </div>

        {/* 사용자 프로필 섹션 */}
        <div className="px-4 py-3 border-t border-gray-700">
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

            {/* 로그아웃 버튼 */}
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
    </div>
  );
}

export default AdminSidebar;
