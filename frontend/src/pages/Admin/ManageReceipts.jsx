import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from '../../services/api';
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
  const [totalCount, setTotalCount] = useState(0);
  
  // 사용자 정보 상태
  const [userName, setUserName] = useState("관리자");
  
  // 영수증 데이터 상태
  const [receipts, setReceipts] = useState([]);
  
  // 날짜 필터 상태
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // 팝업 상태 및 이미지 URL + 현재 영수증 데이터
  const [popupImageUrl, setPopupImageUrl] = useState(null);
  const [popupReceipt, setPopupReceipt] = useState(null);

  // 팝업 닫기 함수
  const closePopup = () => {
    setPopupImageUrl(null);
    setPopupReceipt(null);
  };

  // 페이지 로드 시 사용자 정보와 영수증 목록 조회
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUserInfo();
      fetchReceipts();
    } else {
      console.log('토큰이 없어 API 호출을 건너뜁니다.');
    }
  }, []);

  // 날짜 필터 변경 시 자동 검색
  useEffect(() => {
    // 날짜가 변경되었을 때만 실행
    if (startDate || endDate) {
      // 약간의 지연을 두어 상태 업데이트가 완료된 후 검색 실행
      const timer = setTimeout(async () => {
        try {
          // 데이터를 미리 로드
          const params = new URLSearchParams();
          params.append("page", "1");
          params.append("page_size", "10");
          
          if (startDate) {
            params.append("start_date", startDate);
          }
          if (endDate) {
            params.append("end_date", endDate);
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
          
          const response = await api.get(`/admin/receipts/?${params.toString()}`);
          
          if (response.data.success && response.data.data) {
            const receiptsData = response.data.data.receipts || [];
            // 깜빡임 완전 방지: React 18의 배치 업데이트 활용
            React.startTransition(() => {
              setReceipts(receiptsData);
              setTotalPages(response.data.data.total_pages || 1);
              setTotalCount(response.data.data.total_count || 0);
              setCurrentPage(1);
            });
          }
        } catch (error) {
          console.error("날짜 필터 검색 실패:", error);
        }
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [startDate, endDate, searchTerm, searchType]); // eslint-disable-line react-hooks/exhaustive-deps

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
  const fetchReceipts = useCallback(async (page = 1, showLoading = true) => {
    try {
      // 토큰 체크
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('토큰이 없어 API 호출을 건너뜁니다.');
        return;
      }

      if (showLoading) {
        setIsLoading(true);
      }
      setError("");
      
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
      
      const response = await api.get(`/admin/receipts/?${params.toString()}`);

      // Axios 응답 처리 (response.ok는 fetch() API의 속성)
      console.log('API 응답:', response);
      console.log('응답 상태:', response.status);
      console.log('응답 헤더:', response.headers);
      
      const data = response.data;  // Axios에서는 response.data
      console.log('API 응답 데이터:', data);
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
        setTotalCount(data.data.total_count || 0);
        setCurrentPage(page);
      } else {
        throw new Error(response.data.message || 'API 응답 오류');
      }
    } catch (error) {
      console.error("영수증 목록 조회 실패:", error);
      setError(`영수증 목록을 불러오는데 실패했습니다: ${error.message}`);
      
      // 개발 환경에서만 더미 데이터 표시
      if (process.env.NODE_ENV === 'development') {
        setReceipts([
          { name: "홍길동", dept: "개발", created_at: "2024-01-01", amount: "50000", status: "승인", file_path: "sample1.jpg" },
          { name: "김철수", dept: "영업", created_at: "2024-01-02", amount: "30000", status: "대기", file_path: "sample2.jpg" },
        ]);
      } else {
        setReceipts([]);
      }
    } finally {
      setIsLoading(false);
    }
  }, [startDate, endDate, searchTerm, searchType]);

  // 테이블 컬럼 정의
  const columns = [
    { 
      header: "부서", 
      accessor: "dept",
      cell: (value) => value || "정보 없음"
    },
    { 
      header: "이름", 
      accessor: "name",
      cell: (value) => value || "정보 없음"
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
        const fileExt = value.split('.').pop()?.toLowerCase();
        const isImage = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(fileExt);

        if (isImage) {
          return (
            <button
              onClick={() => {
                setPopupImageUrl(value);

                // extracted_text 파싱
                let parsedExtractedText = {};
                try {
                  if (typeof row.extracted_text === "string") {
                    parsedExtractedText = JSON.parse(row.extracted_text.replace(/'/g, '"'));
                  } else {
                    parsedExtractedText = row.extracted_text;
                  }
                } catch (err) {
                  console.error("extracted_text 파싱 실패:", err);
                }

                setPopupReceipt({
                  row,
                  extracted_text: parsedExtractedText
                });
              }}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-3 rounded text-sm transition-colors"
            >
              이미지 크게 보기
            </button>
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
          minute: '2-digit',
          hour12: true
        });
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

  // 검색 조건 초기화
  const handleClearSearch = () => {
    setSearchTerm("");
    setSearchType("name");
    setStartDate("");
    setEndDate("");
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
    // 날짜 유효성 검사
    if (start && end && start > end) {
      alert("시작일은 종료일보다 이전이어야 합니다.");
      return;
    }
    
    setStartDate(start);
    setEndDate(end);
    setCurrentPage(1);
    fetchReceipts(1);
  };

  // 날짜 필터만 초기화
  const handleClearDateFilter = () => {
    setStartDate("");
    setEndDate("");
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



  // 포맷팅된 데이터 생성
  const formattedReceipts = receipts.map(receipt => ({
    ...receipt,
    amount: formatAmount(receipt.amount),
    // created_at: formatDate(receipt.created_at),
    // previewOpen: previewStates[receipt.receipt_id] || false
  }));

  // 엑셀 다운로드 핸들러
  const handleExcelDownload = async () => {
    try {
      // 쿼리 파라미터 구성 (필터, 날짜 등)
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (searchTerm.trim()) {
        if (searchType === 'status') params.append('reported_yn', searchTerm.trim());
        else if (searchType === 'name') params.append('name', searchTerm.trim());
        else if (searchType === 'dept') params.append('dept', searchTerm.trim());
      }

      // 엑셀 다운로드 API 호출
      const token = localStorage.getItem('access_token');
      const response = await api.get(`/admin/receipts/download?${params.toString()}`, {
        responseType: 'blob',
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // 파일 다운로드 처리
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', '영수증목록.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("엑셀 다운로드 실패:", error);
      alert("엑셀 다운로드 중 오류가 발생했습니다.");
    }
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
            onClearDateFilter={handleClearDateFilter}
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
            onClearSearch={handleClearSearch}
          />
        </div>
        
        {/* 엑셀 다운로드 버튼 */}
        <div className="flex justify-between items-center mb-4">
          {/* 날짜 필터 정보 및 초기화 버튼 */}
          {(startDate || endDate) && (
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-600">
                기간: {startDate ? new Date(startDate).toLocaleDateString('ko-KR') : '시작일'} ~ {endDate ? new Date(endDate).toLocaleDateString('ko-KR') : '종료일'}
              </span>
              <button
                onClick={handleClearDateFilter}
                className="text-xs text-red-600 hover:text-red-800 underline"
              >
                날짜 필터 초기화
              </button>
            </div>
          )}
          
          <button
            onClick={handleExcelDownload}
            className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded shadow transition-colors"
          >
            엑셀 다운로드
          </button>
        </div>

        {/* 로딩 상태 */}
        {isLoading ? (
          <div className="flex justify-center items-center py-8">
            <div className="text-gray-500">영수증 목록을 불러오는 중...</div>
          </div>
        ) : (
          <>
            {/* 검색 결과 요약 */}
            {!error && receipts.length > 0 && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex justify-between items-center">
                  <p className="text-sm text-green-800">
                    총 <span className="font-medium">{totalCount}</span>건의 영수증을 찾았습니다.
                    {(startDate || endDate) && (
                      <span className="ml-2 text-green-600">
                        (기간: {startDate ? new Date(startDate).toLocaleDateString('ko-KR') : '시작일'} ~ {endDate ? new Date(endDate).toLocaleDateString('ko-KR') : '종료일'})
                      </span>
                    )}
                  </p>
                </div>
              </div>
            )}
            
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

        {/* 팝업 이미지 미리보기 */}
        {popupImageUrl && popupReceipt && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60"
            onClick={closePopup}
          >
            <div
              className="bg-white rounded-lg shadow-lg p-4 relative flex flex-col md:flex-row items-center"
              style={{ maxWidth: '90vw', maxHeight: '90vh' }}
              onClick={e => e.stopPropagation()}
            >
              <button
                onClick={closePopup}
                className="absolute top-2 right-2 text-gray-700 hover:text-red-500 text-xl font-bold"
                aria-label="닫기"
              >
                ×
              </button>
              {/* 이미지: 왼쪽 */}
              <div className="flex-shrink-0 flex items-center justify-center md:mr-8 mb-6 md:mb-0">
                <img
                  src={popupImageUrl}
                  alt="영수증 이미지"
                  className="max-w-[40vw] max-h-[70vh] rounded"
                  style={{ display: 'block' }}
                />
              </div>
              {/* 정보: 오른쪽 */}
              <div className="w-full md:w-[420px] bg-gray-50 rounded-lg p-4 border">
                <div className="mb-2 text-base text-gray-800">
                  <span className="font-semibold">결제처: </span>
                  {popupReceipt.extracted_text?.결제처 || "정보 없음"}
                </div>
                <div className="mb-2 text-base text-gray-800">
                  <span className="font-semibold">결제일시: </span>
                  {popupReceipt.extracted_text?.결제일시 || "정보 없음"}
                </div>
                <div className="mb-2 text-base text-gray-800">
                  <span className="font-semibold">카드번호: </span>
                  {popupReceipt.extracted_text?.카드정보 || "정보 없음"}
                </div>
                <div className="mb-2 text-base text-gray-800">
                  <span className="font-semibold">품목 정보: </span>
                  {Array.isArray(popupReceipt.extracted_text?.품목) && popupReceipt.extracted_text?.품목.length > 0 ? (
                    <ul className="mt-1 space-y-1 list-disc list-inside">
                      {popupReceipt.extracted_text?.품목.map((item, idx) => (
                        <li key={idx} className="text-sm text-gray-700">
                          {item.품명} x{item.수량}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <span className="text-gray-400">품목 정보 없음</span>
                  )}
                </div>
                <div className="mb-2 text-base text-gray-800">
                  <span className="font-semibold">합계: </span>
                  {popupReceipt.extracted_text?.총합계 || "정보 없음"}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ManageReceipts;