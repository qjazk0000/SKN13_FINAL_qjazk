import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AdminSidebar from "./components/AdminSidebar.jsx";
import DateSelectBar from "./components/DateSelectBar.jsx";
import SearchBar from "./components/SearchBar.jsx";
import DataTable from "./components/DataTable.jsx";
import Pagination from "./components/Pagination.jsx";
import { authService } from "../../services/authService";

function ManageReceipts() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("name");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTab, setSelectedTab] = useState("manage-receipt");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [totalPages, setTotalPages] = useState(1);
  
  // 사용자 정보 상태
  const [userName, setUserName] = useState("관리자");
  
  // 영수증 데이터 상태
  const [receipts, setReceipts] = useState([]);
  
  // 날짜 필터 상태
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // 페이지 로드 시 사용자 정보와 영수증 목록 조회
  useEffect(() => {
    loadUserInfo();
    fetchReceipts();
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

  // 영수증 목록 조회
  const fetchReceipts = async (page = 1) => {
    try {
      setIsLoading(true);
      setError("");
      
      const token = authService.getToken();
      if (!token) {
        throw new Error('로그인이 필요합니다.');
      }
      
      // 쿼리 파라미터 구성
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('page_size', '10');
      
      if (startDate) {
        params.append('start_date', startDate);
      }
      if (endDate) {
        params.append('end_date', endDate);
      }
      
      // 검색 필터 적용
      if (searchTerm.trim()) {
        if (searchType === 'status') {
          params.append('reported_yn', searchTerm.trim());
        } else if (searchType === 'name') {
          params.append('name', searchTerm.trim());
        } else if (searchType === 'dept') {
          params.append('dept', searchTerm.trim());
        }
      }
      
      const response = await fetch(`/api/admin/receipts/list/?${params.toString()}`, {
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
      console.log('API 응답:', data);
      
      if (data.success && data.data) {
        setReceipts(data.data.receipts || []);
        setTotalPages(data.data.total_pages || 1);
        setCurrentPage(page);
      } else {
        throw new Error(data.message || 'API 응답 오류');
      }
    } catch (error) {
      console.error("영수증 목록 조회 실패:", error);
      setError(`영수증 목록을 불러오는데 실패했습니다: ${error.message}`);
      
      // 개발 환경에서만 더미 데이터 표시
      if (process.env.NODE_ENV === 'development') {
        setReceipts([
          {
            name: "홍길동",
            dept: "개발팀",
            created_at: "2024-01-15T10:00:00",
            amount: 50000,
            status: "승인완료",
            file_path: "https://example.com/receipt1.pdf",
            receipt_id: "1",
            user_login_id: "hong"
          },
          {
            name: "김철수",
            dept: "영업팀",
            created_at: "2024-01-14T14:30:00",
            amount: 75000,
            status: "승인대기",
            file_path: "https://example.com/receipt2.pdf",
            receipt_id: "2",
            user_login_id: "kim"
          }
        ]);
        setTotalPages(1);
      } else {
        setReceipts([]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 테이블 컬럼 정의
  const columns = [
    { header: "이름", accessor: "name" },
    { header: "부서", accessor: "dept" },
    { header: "제출일자", accessor: "created_at" },
    { header: "금액", accessor: "amount" },
    { header: "상태", accessor: "status" },
    { 
      header: "영수증 보기", 
      accessor: "file_path",
      cell: (value) => (
        <button
          onClick={() => window.open(value, '_blank')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded text-sm"
        >
          보기
        </button>
      )
    }
  ];

  // 검색 옵션 정의
  const searchOptions = [
    { value: "name", label: "이름" },
    { value: "dept", label: "부서" },
    { value: "status", label: "승인 여부" }
  ];

  // 검색 처리 함수
  const handleSearch = () => {
    console.log(`검색 유형: ${searchType}, 검색어: ${searchTerm}`);
    setCurrentPage(1);
    fetchReceipts(1);
  };

  // 페이지 변경 처리 함수
  const handlePageChange = (page) => {
    setCurrentPage(page);
    fetchReceipts(page);
  };

  // 날짜 변경 처리 함수
  const handleDateChange = (start, end) => {
    setStartDate(start);
    setEndDate(end);
    setCurrentPage(1);
    fetchReceipts(1);
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
      case "chat-reports":
        navigate("/admin/chat-reports");
        break;
      case "manage-receipt":
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

  // 금액 포맷팅 함수
  const formatAmount = (amount) => {
    return new Intl.NumberFormat('ko-KR').format(amount) + '원';
  };

  // 날짜 포맷팅 함수
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
  };

  // 포맷팅된 데이터 생성
  const formattedReceipts = receipts.map(receipt => ({
    ...receipt,
    amount: formatAmount(receipt.amount),
    created_at: formatDate(receipt.created_at)
  }));

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
        <h1 className="text-2xl font-bold mb-6">영수증 관리</h1>
        
        {/* 에러 메시지 */}
        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
        
        {/* 기간 선택 바 */}
        <div className="mb-6">
          <DateSelectBar 
            onDateChange={handleDateChange}
            startDate={startDate}
            endDate={endDate}
          />
        </div>
        
        {/* 검색 바 */}
        <div className="mb-6">
          <SearchBar
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            onSearch={handleSearch}
            searchType={searchType}
            setSearchType={setSearchType}
            searchOptions={searchOptions}
          />
        </div>
        
        {/* 로딩 상태 */}
        {isLoading ? (
          <div className="flex justify-center items-center py-8">
            <div className="text-gray-500">영수증 목록을 불러오는 중...</div>
          </div>
        ) : (
          <>
            {/* 데이터 테이블 */}
            <div className="mb-6">
              <DataTable columns={columns} data={formattedReceipts} />
            </div>
            
            {/* 페이지네이션 */}
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

export default ManageReceipts;
