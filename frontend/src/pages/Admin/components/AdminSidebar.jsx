import React from "react";
import { Link } from "react-router-dom";

function AdminSidebar() {
  return (
    <div className="w-64 bg-gray-800 text-white min-h-screen p-4">
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
  );
}

export default AdminSidebar;
