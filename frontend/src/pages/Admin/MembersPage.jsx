import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AdminSidebar from "./components/AdminSidebar.jsx";
import SearchBar from "./components/SearchBar";
import DataTable from "./components/DataTable";
import Pagination from "./components/Pagination";
import { authService } from "../../services/authService";

function MembersPage() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("name");
  const [members, setMembers] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTab, setSelectedTab] = useState("members");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [totalPages, setTotalPages] = useState(1);
  
  // 사용자 정보 상태
  const [userName, setUserName] = useState("관리자");

  // 페이지 로드 시 사용자 정보와 회원 목록 조회
  useEffect(() => {
    loadUserInfo();
    fetchMembers();
  }, []);

  // 사용자 정보 로드
  const loadUserInfo = async () => {
    try {
      const currentUser = authService.getCurrentUser();
      if (currentUser && currentUser.name) {
        setUserName(currentUser.name);
      }
    } catch (error) {
      console.error("사용자 정보 로드 실패:", error);
    }
  };

  // 회원 목록 조회
  const fetchMembers = async (filter = "", page = 1) => {
    try {
      setIsLoading(true);
      setError("");
      
      const token = authService.getToken();
      if (!token) {
        throw new Error('로그인이 필요합니다.');
      }
      
      const response = await fetch(`/api/admin/users/?filter=${encodeURIComponent(filter)}&page=${page}&page_size=10`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error(`잘못된 응답 형식: ${contentType}. API 엔드포인트를 확인해주세요.`);
      }

      const data = await response.json();
      console.log('API 응답:', data); // 디버깅용 로그
      
      if (data.success && data.data) {
        setMembers(data.data.users || []);
        setTotalPages(data.data.total_pages || 1);
        setCurrentPage(1);
      } else {
        throw new Error(data.message || 'API 응답 오류');
      }
    } catch (error) {
      console.error("회원 목록 조회 실패:", error);
      setError(`회원 목록을 불러오는데 실패했습니다: ${error.message}`);
      
      // 개발 환경에서만 더미 데이터 표시
      if (process.env.NODE_ENV === 'development') {
        setMembers([
          { dept: "개발", name: "홍길동", user_login_id: "hong", rank: "사원", email: "hong@test.com", use_yn: "Y", created_dt: "2024-01-01" },
          { dept: "영업", name: "김철수", user_login_id: "kim", rank: "대리", email: "kim@test.com", use_yn: "Y", created_dt: "2024-01-02" },
        ]);
      } else {
        setMembers([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const columns = [
    { header: "부서", accessor: "dept" },
    { header: "이름", accessor: "name" },
    { header: "로그인 ID", accessor: "user_login_id" },
    { header: "직급", accessor: "rank" },
    { header: "이메일", accessor: "email" },
    { header: "계정 활성 여부", accessor: "use_yn" },
    { header: "가입일", accessor: "created_dt" },
  ];

  const searchOptions = [
    { value: "dept", label: "부서" },
    { value: "name", label: "이름" },
    { value: "user_login_id", label: "로그인 ID" },
    { value: "rank", label: "직급" },
    { value: "email", label: "이메일" },
  ];

   const handleSearch = () => {
    console.log(`검색 유형: ${searchType}, 검색어: ${searchTerm}`);
   
    // 검색 필터 구성
    let filter = "";
    if (searchTerm.trim()) {
      filter = `${searchType}:${searchTerm.trim()}`;
    }
    
    // API 호출로 회원 목록 조회 (페이지 1로 리셋)
    setCurrentPage(1);
    fetchMembers(filter, 1);

  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    // 페이지 변경 시 현재 검색 조건으로 데이터 재조회
    let filter = "";
    if (searchTerm.trim()) {
      filter = `${searchType}:${searchTerm.trim()}`;
    }
    fetchMembers(filter, page);
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
      case "chat-reports":
        navigate("/admin/chat-reports");
        break;
      case "manage-receipt":
        navigate("/admin/manage-receipts");
        break;
      case "members":
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
        <h1 className="text-2xl font-bold mb-4">회원 관리</h1>
        
        {/* 에러 메시지 */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
        <SearchBar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          onSearch={handleSearch}
          searchType={searchType}
          setSearchType={setSearchType}
          searchOptions={searchOptions}
        />
        {/* 로딩 상태 */}
        {isLoading ? (
          <div className="flex justify-center items-center py-8">
            <div className="text-gray-500">회원 목록을 불러오는 중...</div>
          </div>
        ) : (
          <>
            <DataTable columns={columns} data={members} />
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default MembersPage;
