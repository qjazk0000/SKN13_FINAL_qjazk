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

  // 이미지 미리보기 토글 상태
  const [previewStates, setPreviewStates] = useState({});

  // 이미지 미리보기 토글 함수
  const togglePreview = (receiptId) => {
    setPreviewStates(prev => ({
      ...prev,
      [receiptId]: !prev[receiptId]
    }));
  };

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
      
      const response = await fetch(`/api/admin/receipts/?${params.toString()}`, {
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
      console.log('영수증 데이터:', data.data?.receipts);
      
      if (data.success && data.data) {
        const receiptsData = data.data.receipts || [];
        console.log('처리할 영수증 데이터:', receiptsData);
        receiptsData.forEach((receipt, index) => {
          console.log(`영수증 ${index + 1}:`, receipt);
          console.log(`영수증 ${index + 1} items_info:`, receipt.items_info);
          console.log(`영수증 ${index + 1} extracted_text:`, receipt.extracted_text);
        });
        
        setReceipts(receiptsData);
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
            file_path: "https://example.com/receipt1.jpg",
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
    { 
      header: "이름", 
      accessor: "name",
      cell: (value) => value || "정보 없음"
    },
    { 
      header: "부서", 
      accessor: "dept",
      cell: (value) => value || "정보 없음"
    },
    { 
      header: "제출일자", 
      accessor: "created_at",
      cell: (value) => {
        if (!value) return "정보 없음";
        const date = new Date(value);
        return date.toLocaleString('ko-KR', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
    },
    { 
      header: "금액", 
      accessor: "amount",
      cell: (value) => {
        // null, undefined, 빈 문자열 체크
        if (value === null || value === undefined || value === '') {
          return "정보 없음";
        }
        
        // 문자열로 변환
        const stringValue = String(value);
        
        // 이미 "원"이 포함된 포맷된 문자열인지 확인
        if (stringValue.includes('원')) {
          // "원" 제거하고 쉼표 제거 후 숫자 추출
          const cleanValue = stringValue.replace(/[원,]/g, '');
          const numValue = parseFloat(cleanValue);
          
          if (isNaN(numValue)) {
            return "정보 없음";
          }
          
          // 한국어 숫자 포맷으로 다시 변환
          return new Intl.NumberFormat('ko-KR').format(numValue) + "원";
        } else {
          // 일반 숫자 문자열인 경우
          const numValue = parseFloat(stringValue);
          
          if (isNaN(numValue)) {
            return "정보 없음";
          }
          
          return new Intl.NumberFormat('ko-KR').format(numValue) + "원";
        }
      }
    },
    { 
      header: "상태", 
      accessor: "status",
      cell: (value) => {
        const statusMap = {
          'pending': '대기',
          'approved': '승인',
          'rejected': '반려',
          'processed': '처리완료'
        };
        return statusMap[value] || value;
      }
    },
    { 
      header: "영수증 보기", 
      accessor: "file_path",
      cell: (value, row) => {
        if (!value) return <span className="text-gray-400">파일 없음</span>;
        
        // 파일 확장자 확인
        const fileExt = value.split('.').pop()?.toLowerCase();
        const isImage = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExt);
        const receiptId = row.receipt_id;
        const isPreviewOpen = previewStates[receiptId];
        
        if (isImage) {
          return (
            <div className="flex flex-col items-center space-y-2">
              <button
                onClick={() => togglePreview(receiptId)}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded text-sm transition-colors"
              >
                {isPreviewOpen ? '접기' : '미리보기'}
              </button>
              
              {/* 이미지 미리보기 */}
              {isPreviewOpen && (
                <div className="w-full max-w-xs bg-white border border-gray-300 rounded overflow-hidden">
                  <div className="p-2">
                    <img
                      src={value}
                      alt="영수증 이미지"
                      className="w-full max-h-48 object-contain"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                    <div className="hidden text-center text-gray-500 text-xs">
                      <p>이미지를 불러올 수 없습니다</p>
                      <a 
                        href={value} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:underline"
                      >
                        새 창에서 보기
                      </a>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        } else {
          return (
            <a
              href={value}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded text-sm transition-colors"
            >
              열기
            </a>
          );
        }
      }
    },
    {
      header: "품목 정보",
      accessor: "items_info",
      cell: (value, row) => {
        const receiptId = row.receipt_id;
        const isPreviewOpen = previewStates[receiptId];
        const itemsInfo = row.items_info || [];
        
        // 미리보기가 열려있을 때만 품목 정보 표시
        if (!isPreviewOpen) {
          return <span className="text-gray-400">-</span>;
        }
        
        if (itemsInfo.length === 0) {
          return <span className="text-gray-400">품목 정보 없음</span>;
        }
        
        return (
          <div className="space-y-1">
            {itemsInfo.map((item, index) => (
              <div key={index} className="text-xs bg-gray-50 px-2 py-1 rounded border whitespace-nowrap">
                {item}
              </div>
            ))}
          </div>
        );
      }
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
    created_at: formatDate(receipt.created_at),
    previewOpen: previewStates[receipt.receipt_id] || false
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
