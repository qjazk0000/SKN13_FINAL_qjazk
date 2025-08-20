import React from "react";
import { Link } from "react-router-dom";

function AdminSidebar({ 
  userName,
  onUserNameClick, 
  onLogout, 
  onGoToChat 
}) {

  const initials = userName?.[0] || "U";
  const displayName = userName || "사용자";

  return (
    <div className="w-64 bg-gray-800 text-white min-h-screen flex flex-col">
      {/* 상단 메뉴 */}
      <div className="p-4">
        <h2 className="text-xl font-bold mb-6">관리자 메뉴</h2>
        <ul className="space-y-4">
          <li>
            <Link to="/admin/members" className="hover:text-blue-400">
              회원 관리
            </Link>
          </li>
          <li>
            <Link to="/admin/chat-reports" className="hover:text-blue-400">
              채팅 신고 내역
            </Link>
          </li>
        </ul>
      </div>
        
      {/* 하단 사용자명 + 채팅 화면 버튼 + 로그아웃 */}
      <div className="mt-auto px-4 py-3 border-t border-gray-700 flex flex-col gap-2">
        {/* 채팅 화면으로 돌아가기 버튼 */}
        <button
          type="button"
          onClick={onGoToChat}
          className="w-full py-2 px-4 rounded-md bg-gray-600 hover:bg-gray-500 text-white text-left flex items-center gap-2 transition"
        >
          채팅 화면으로 이동
        </button>

        {/* 사용자 정보 + 로그아웃 */}
        <div className="flex items-center justify-between mt-2">
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

export default AdminSidebar;
