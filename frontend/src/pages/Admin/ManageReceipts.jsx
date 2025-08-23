import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AdminSidebar from "./components/AdminSidebar.jsx";
import DateSelectBar from "./components/DateSelectBar.jsx";
import SearchBar from "./components/SearchBar.jsx";
import DataTable from "./components/DataTable.jsx";
import Pagination from "./components/Pagination.jsx";

function ManageReceipts() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("name");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTab, setSelectedTab] = useState("manage-receipt");
  
  // 사용자 정보 상태 (실제로는 API에서 가져와야 함)
  const [userName, setUserName] = useState("관리자");
  
  // 영수증 데이터 상태
  const [receipts, setReceipts] = useState([
    {
      id: 1,
      name: "홍길동",
      dept: "개발팀",
      submit_date: "2024-01-15",
      amount: 50000,
      status: "승인완료",
      receipt_url: "https://example.com/receipt1.pdf"
    },
    {
      id: 2,
      name: "김철수",
      dept: "영업팀",
      submit_date: "2024-01-14",
      amount: 75000,
      status: "승인대기",
      receipt_url: "https://example.com/receipt2.pdf"
    },
    {
      id: 3,
      name: "이영희",
      dept: "인사팀",
      submit_date: "2024-01-13",
      amount: 30000,
      status: "승인완료",
      receipt_url: "https://example.com/receipt3.pdf"
    },
    {
      id: 4,
      name: "박민수",
      dept: "기획팀",
      submit_date: "2024-01-12",
      amount: 120000,
      status: "반려",
      receipt_url: "https://example.com/receipt4.pdf"
    },
    {
      id: 5,
      name: "정수진",
      dept: "마케팅팀",
      submit_date: "2024-01-11",
      amount: 45000,
      status: "승인완료",
      receipt_url: "https://example.com/receipt5.pdf"
    }
  ]);

  // 테이블 컬럼 정의
  const columns = [
    { header: "이름", accessor: "name" },
    { header: "부서", accessor: "dept" },
    { header: "제출일자", accessor: "submit_date" },
    { header: "금액", accessor: "amount" },
    { header: "상태", accessor: "status" },
    { 
      header: "영수증 보기", 
      accessor: "receipt_url",
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
    // TODO: searchType과 searchTerm을 활용해 API 호출 및 필터링 처리
  };

  // 페이지 변경 처리 함수
  const handlePageChange = (page) => {
    setCurrentPage(page);
    console.log(`페이지 ${page}로 이동`);
    // TODO: API 호출로 페이지 데이터 불러오기
  };

  // 사용자명 클릭 핸들러
  const handleUserNameClick = () => {
    console.log("마이페이지로 이동");
    // TODO: 마이페이지로 이동하는 로직 구현
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

  // 포맷팅된 데이터 생성
  const formattedReceipts = receipts.map(receipt => ({
    ...receipt,
    amount: formatAmount(receipt.amount)
  }));

  return (
    <div className="flex">
      <AdminSidebar 
        userName={userName}
        onUserNameClick={handleUserNameClick}
        selectedTab={selectedTab}
        onTabSelect={handleTabSelect}
        onChatPageClick={handleChatPageClick}
      />
      <div className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-6">영수증 관리</h1>
        
        {/* 기간 선택 바 */}
        <div className="mb-6">
          <DateSelectBar />
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
        
        {/* 데이터 테이블 */}
        <div className="mb-6">
          <DataTable columns={columns} data={formattedReceipts} />
        </div>
        
        {/* 페이지네이션 */}
        <Pagination
          currentPage={currentPage}
          totalPages={5}
          onPageChange={handlePageChange}
        />
      </div>
    </div>
  );
}

export default ManageReceipts;
