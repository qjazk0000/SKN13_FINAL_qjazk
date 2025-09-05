import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../../services/authService";
import api from "../../services/api";
import AdminSidebar from "./components/AdminSidebar.jsx";
import SearchBar from "./components/SearchBar";
import DataTable from "./components/DataTable";
import Pagination from "./components/Pagination";

function MembersPage() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("name");
  const [members, setMembers] = useState([]);
  const [updatedUseYn, setUpdatedUseYn] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTab, setSelectedTab] = useState("members");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [totalPages, setTotalPages] = useState(1);
  
  // 사용자 정보 상태
  const [userName, setUserName] = useState("관리자");

  // 페이지 로드 시 사용자 정보와 회원 목록 조회
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUserInfo();
      fetchMembers();
    } else {
      console.log('토큰이 없어 API 호출을 건너뜁니다.');
    }
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
      // 토큰 체크
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('토큰이 없어 API 호출을 건너뜁니다.');
        return;
      }

      console.log('fetchMembers 시작:', { filter, page, token: token.substring(0, 20) + '...' });

      setIsLoading(true);
      setError("");
      
      const url = `/admin/users/?filter=${encodeURIComponent(filter)}&page=${page}&page_size=10`;
      console.log('API 요청 URL:', url);
      
      const response = await api.get(url);
      console.log('API 응답 전체:', response);
      console.log('API 응답 상태:', response.status);
      console.log('API 응답 헤더:', response.headers);

      const data = response.data;
      console.log('API 응답 데이터:', data);
      
      if (data.success && data.data) {
        setMembers(data.data.users || []);
        setTotalPages(data.data.total_pages || 1);
        setCurrentPage(page);
        console.log('회원 목록 설정 완료:', data.data.users?.length || 0, '명');
      } else {
        console.error('API 응답이 성공이 아님:', data);
        throw new Error(data.message || 'API 응답 오류');
      }
    } catch (error) {
      console.error("회원 목록 조회 실패:", error);
      console.error("에러 상세:", {
        message: error.message,
        response: error.response,
        status: error.response?.status,
        data: error.response?.data
      });
      
      setError(`회원 목록을 불러오는데 실패했습니다: ${error.message}`);
      
      // 개발 환경에서만 더미 데이터 표시
      if (process.env.NODE_ENV === 'development') {
        console.log('개발 환경: 더미 데이터 표시');
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

  const handleChangeUseYn = (userId, newValue) => {
    setUpdatedUseYn(prev => ({ ...prev, [userId]: newValue }));
    setMembers(prev =>
      prev.map(member =>
        member.user_login_id === userId ? { ...member, use_yn: newValue } : member
      )
    );
  };

  const handleSaveChanges = async () => {
    try {
      const payload = Object.entries(updatedUseYn).map(([user_login_id, use_yn]) => ({
        user_login_id,
        use_yn
      }));

      const token = localStorage.getItem("access_token");
      const response = await api.post("admin/users/update_use_yn/", payload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.success) {
        alert("변경 사항이 저장되었습니다.");
        setUpdatedUseYn({}); // 변경 내역 초기화
      } else {
        alert("저장 실패: " + response.data.message);
      }
    } catch (err) {
      console.error(err);
      alert("저장 중 오류가 발생했습니다.");
    }
  };


  const columns = [
    { header: "부서", accessor: "dept" },
    { header: "이름", accessor: "name" },
    { header: "로그인 ID", accessor: "user_login_id" },
    { header: "직급", accessor: "rank" },
    { header: "이메일", accessor: "email" },
    // { header: "계정 활성 여부", accessor: "use_yn" },
    {
    header: "계정 활성 여부",
    accessor: "use_yn",
    cell: (value, row) => (
      <select
        value={value}
        onChange={(e) => handleChangeUseYn(row.user_login_id, e.target.value)}
        className="border rounded p-1 text-center w-20"
      >
        <option value="Y">Y</option>
        <option value="N">N</option>
      </select>
    ),
  },
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
    
    // API 호출로 회원 목록 조회 
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
    <div className="flex h-screen">
      <div className="w-72 bg-gray-800 text-white flex-shrink-0 h-screen">
        <AdminSidebar 
        userName={userName}
        selectedTab={selectedTab}
        onTabSelect={handleTabSelect}
        onChatPageClick={handleChatPageClick}
      />
      </div>
      <div className="flex-1 overflow-y-auto p-6">
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
        <div className="mb-4 flex justify-end">
          <button
            onClick={handleSaveChanges}
            disabled={Object.keys(updatedUseYn).length === 0}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
          >
            변경 사항 저장
          </button>
        </div>

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
