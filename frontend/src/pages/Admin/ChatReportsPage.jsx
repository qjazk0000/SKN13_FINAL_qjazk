import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import dayjs from "dayjs";
import AdminSidebar from "./components/AdminSidebar.jsx";
import SearchBar from "./components/SearchBar";
import DataTable from "./components/DataTable";
import Pagination from "./components/Pagination";
import DateSelectBar from "./components/DateSelectBar";
import { authService } from "../../services/authService";

function ChatReportsPage() {

  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("chat_id");
  const now = dayjs().format("YYYY-MM-DD HH:mm:ss");

  const [members, setMembers] = useState([
    { 
        chat_id: "chat0101", 
        user_id: "dept0101", 
        session_id: "0101", 
        chat_date: dayjs().format("YYYY-MM-DD HH:mm:ss"),
        user_input: "추석 상여금 알려줘", 
        response:"추석 상여금의 대한 응답입니다." 
    },
    { 
        chat_id: "chat0102", 
        user_id: "sales0101", 
        session_id: "0102", 
        chat_date: dayjs().format("YYYY-MM-DD HH:mm:ss"),
        user_input: "추석 상여금 알려줘", 
        response:"추석 상여금의 대한 응답입니다." 
    },
  ]);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTab, setSelectedTab] = useState("chat-reports");  
  // 사용자 정보 상태 (실제로는 API에서 가져와야 함)
  const [userName, setUserName] = useState("관리자");


  const columns = [
    { header: "채팅 ID", accessor: "chat_id" },
    { header: "사용자 ID", accessor: "user_id" },
    { header: "세션 ID", accessor: "session_id" },
    { header: "대화 날짜", accessor: "chat_date" },
    { header: "사용자 입력", accessor: "user_input" },
    { header: "LLM 응답", accessor: "response" },
  ];

  const searchOptions = [
    { value: "chat_id", label: "채팅 ID" },
    { value: "user_id", label: "사용자 ID" },
    { value: "session_id", label: "세션 ID" },
    { value: "chat_input", label: "사용자 입력" },
    { value: "response", label: "LLM 응답" },
  ];

   const handleSearch = () => {
    console.log(`검색 유형: ${searchType}, 검색어: ${searchTerm}`);
    // TODO: searchType과 searchTerm을 활용해 API 호출 및 필터링 처리
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    // TODO: API 호출로 페이지 데이터 불러오기
  };

  // 사용자명 클릭 핸들러
  const handleUserNameClick = () => {
    console.log("마이페이지로 이동");
    // TODO: 마이페이지로 이동하는 로직 구현
  };

  // 로그아웃 핸들러
  const handleLogout = () => {
    console.log("로그아웃");
    // TODO: 로그아웃 로직 구현
  };

  // 탭 선택 핸들러
  const handleTabSelect = (tabName) => {
    setSelectedTab(tabName);
    
    // 선택된 탭에 따라 해당 페이지로 이동
    switch (tabName) {
      case "members":
        navigate("/admin/members");
        break;
      case "manage-receipt":
        navigate("/admin/manage-receipts");
        break;
      case "chat-reports":
        // 현재 페이지이므로 이동하지 않음
        break;
      default:
        console.log(`알 수 없는 탭: ${tabName}`);
    }
  };

  // 채팅 화면으로 이동 핸들러
  const handleChatPageClick = () => {
    navigate("/chat");
  };

  return (
    <div className="flex">
      <AdminSidebar 
        userName={userName}
        onUserNameClick={handleUserNameClick}
        onLogout={handleLogout}
        selectedTab={selectedTab}
        onTabSelect={handleTabSelect}
        onChatPageClick={handleChatPageClick}
      />
      <div className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-4">대화 신고 내역</h1>
        <DateSelectBar />
        <SearchBar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          onSearch={handleSearch}
          searchType={searchType}
          setSearchType={setSearchType}
          searchOptions={searchOptions}
        />
        <DataTable columns={columns} data={members} />
        <Pagination
          currentPage={currentPage}
          totalPages={5}
          onPageChange={handlePageChange}
        />
      </div>
    </div>
  );
}

export default ChatReportsPage;
