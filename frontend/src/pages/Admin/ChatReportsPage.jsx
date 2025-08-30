import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import AdminSidebar from "./components/AdminSidebar.jsx";
import SearchBar from "./components/SearchBar";
import DataTable from "./components/DataTable";
import Pagination from "./components/Pagination";
import DateSelectBar from "./components/DateSelectBar";
import { authService } from "../../services/authService";
import api from "../../services/api.js";

function ChatReportsPage() {

  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("dept");


  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTab, setSelectedTab] = useState("chat-reports");  
  // 사용자 정보 상태 (실제로는 API에서 가져와야 함)
  const [userName, setUserName] = useState("관리자");

  // 채팅 데이터 상태
  const [chatData, setChatData] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // 날짜 필터 상태
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      loadUserInfo();
      fetchChatReports();
    } else {
      console.log("토큰이 없어 API 호출을 건너뜁니다.");
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
          
          // 검색 조건 처리
          const trimmedSearchTerm = searchTerm.trim();
          if (trimmedSearchTerm) {
            if (searchType === 'dept') {
              params.append("dept", trimmedSearchTerm);
            } else if (searchType === 'name') {
              params.append("name", trimmedSearchTerm);
            } else if (searchType === 'rank') {
              params.append("rank", trimmedSearchTerm);
            } else if (searchType === 'error_type') {
              params.append("error_type", trimmedSearchTerm);
            } else if (searchType === 'reason') {
              params.append("reason", trimmedSearchTerm);
            } else if (searchType === 'remark') {
              params.append("remark", trimmedSearchTerm);
            }
          }
          
          const response = await api.get(`/admin/conversations/reports/?${params.toString()}`);
          
          if (response.data.success) {
            // 깜빡임 완전 방지: React 18의 배치 업데이트 활용
            React.startTransition(() => {
              setChatData(response.data.data.reports);
              setTotalPages(response.data.data.total_pages);
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

  const fetchChatReports = useCallback(async (page = 1, showLoading = true) => {
    try {
      // 토큰 체크
      // const token = localStorage.getItem("access_token");
      // if (!token) {
      //   console.log("토큰이 없어 API 호출을 건너뜁니다.");
      //   return;
      // }

      if (showLoading) {
        setIsLoading(true);
      }
      setError("");

      const params = new URLSearchParams();
      params.append("page", page.toString());
      params.append("page_size", "10");

      if (startDate) {
        params.append("start_date", startDate);
      }
      if (endDate) {
        params.append("end_date", endDate);
      }

      // 검색 조건 처리
      const trimmedSearchTerm = searchTerm.trim();
      
      if (trimmedSearchTerm) {
        if (searchType === 'dept') {
          params.append("dept", trimmedSearchTerm);
        } else if (searchType === 'name') {
          params.append("name", trimmedSearchTerm);
        } else if (searchType === 'rank') {
          params.append("rank", trimmedSearchTerm);
        } else if (searchType === 'error_type') {
          params.append("error_type", trimmedSearchTerm);
        } else if (searchType === 'reason') {
          params.append("reason", trimmedSearchTerm);
        } else if (searchType === 'remark') {
          params.append("remark", trimmedSearchTerm);
        }
      }
      
      const response = await api.get(`/admin/conversations/reports/?${params.toString()}`);

      if (response.data.success) {
        // 백엔드 검색 결과 사용
        setChatData(response.data.data.reports);
        setTotalPages(response.data.data.total_pages);
        setCurrentPage(page);
      } else {
        throw new Error(response.data.message || 'API 응답 오류');
      }
    } catch (error) {
      console.error("채팅 신고 데이터 로드 실패:", error);
      setError("채팅 신고 데이터 로드 실패");
    } finally {
      setIsLoading(false);
    }
  }, [startDate, endDate, searchTerm, searchType]);

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
      header: "직급",
      accessor: "rank",
      cell: (value) => value || "정보 없음"
    },
    {
      header: "사용자 입력",
      accessor: "user_input",
      cell: (value) => value || "정보 없음"
    },
    {
      header: "LLM 응답",
      accessor: "llm_response",
      cell: (value) => value || "정보 없음"
    },
    {
      header: "대화 날짜",
      accessor: "chat_date",
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
      header: "신고 유형",
      accessor: "error_type",
      cell: (value) => {
        const errorTypeMap = {
          'hallucination': '환각',
          'fact_error': '사실 오류',
          'irrelevant': '관련 없음',
          'incomplete': '불완전',
          'other': '기타'
        };
        return errorTypeMap[value] || value || "정보 없음";
      }
    },
    {
      header: "신고 사유",
      accessor: "reason",
      cell: (value) => value || "정보 없음"
    },
    {
      header: "신고 일시",
      accessor: "reported_at",
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
      header: "비고",
      accessor: "remark",
      cell: (value, row) => {
        if (value && value.trim()) {
          return (
            <button
              onClick={() => handleViewFeedback(row.chat_id, value)}
              className="text-blue-600 hover:text-blue-800 underline cursor-pointer"
            >
              피드백 보기
            </button>
          );
        } else {
          return (
            <button
              onClick={() => handleWriteFeedback(row.chat_id)}
              className="text-green-600 hover:text-green-800 underline cursor-pointer"
            >
              피드백 작성
            </button>
          );
        }
      }
    },
  ];

  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [feedbackContent, setFeedbackContent] = useState("");
  const [feedbackMode, setFeedbackMode] = useState("");
  const [currentFeedback, setCurrentFeedback] = useState("");

  // 피드백 보기 핸들러
  const handleViewFeedback = (chatId, feedback) => {
    setSelectedChatId(chatId);
    setCurrentFeedback(feedback);
    setFeedbackMode("view");
    setIsFeedbackModalOpen(true);
  };

  // 피드백 작성 핸들러
  const handleWriteFeedback = (chatId) => {
    setSelectedChatId(chatId);
    setFeedbackContent("");
    setFeedbackMode("write");
    setIsFeedbackModalOpen(true);
  };

  const handleSaveFeedback = async () => {
    try {
      if (!feedbackContent.trim()) {
        alert("피드백 내용을 입력해주세요.");
        return;
      }

      const response = await api.post(`/admin/chat-reports/${selectedChatId}/feedback`, {
        remark: feedbackContent.trim()
      });

      if (response.data.success) {
        alert("피드백이 성공적으로 저장되었습니다.");
        setIsFeedbackModalOpen(false);
        // 테이블 데이터 새로고침
        fetchChatReports(currentPage);
      } else {
        alert("피드백 저장에 실패했습니다.");
      }
    } catch (error) {
      console.error("피드백 저장 실패:", error);
      alert("피드백 저장 중 오류가 발생했습니다.");
    }
  };
  
  // 피드백 모달 달기
  const handleCloseFeedbackModal = () => {
    setIsFeedbackModalOpen(false);
    setSelectedChatId(null);
    setFeedbackContent("");
    setCurrentFeedback("");
    setFeedbackMode("");
  };

          const searchOptions = [
            { value: "dept", label: "부서명" },
            { value: "name", label: "이름" },
            { value: "rank", label: "직급" },
            { value: "error_type", label: "신고 유형" },
            { value: "remark", label: "비고" }
        ];



        // 신고 유형 선택 옵션 (한국어)
        const errorTypeOptions = [
            { value: "불완전", label: "불완전" },
            { value: "환각", label: "환각" },
            { value: "사실 오류", label: "사실 오류" },
            { value: "무관련", label: "무관련" },
            { value: "기타", label: "기타" }
        ];

  const handleDateChange = (start, end) => {
    // 날짜 유효성 검사
    if (start && end && start > end) {
      alert("시작일은 종료일보다 이전이어야 합니다.");
      return;
    }
    
    setStartDate(start);
    setEndDate(end);
    // 날짜 변경 시 1페이지부터 검색 시작
    setCurrentPage(1);
    fetchChatReports(1);
  };

     const handleSearch = () => {
    // 검색어가 없어도 날짜 필터가 있으면 검색 가능
    if (!searchTerm.trim() && !startDate && !endDate) {
      alert("검색어 또는 날짜를 입력해주세요.");
      return;
    }
    
    setCurrentPage(1);
    fetchChatReports(1);
  };

  const handleClearSearch = () => {
    setSearchTerm("");
    setSearchType("dept");
    setStartDate("");
    setEndDate("");
    setCurrentPage(1);
    fetchChatReports(1);
  };

  // 날짜 필터만 초기화
  const handleClearDateFilter = () => {
    setStartDate("");
    setEndDate("");
    setCurrentPage(1);
    fetchChatReports(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    fetchChatReports(page);
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
        selectedTab={selectedTab}
        onTabSelect={handleTabSelect}
        onChatPageClick={handleChatPageClick}
      />
      <div className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-4">대화 신고 내역</h1>
        <DateSelectBar 
          startDate={startDate}
          endDate={endDate}
          onDateChange={handleDateChange}
          onClearDateFilter={handleClearDateFilter}
        />
        <SearchBar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          onSearch={handleSearch}
          searchType={searchType}
          setSearchType={setSearchType}
          searchOptions={searchOptions}
          onClearSearch={handleClearSearch}
          errorTypeOptions={errorTypeOptions}
        />
        
        {isLoading && (
          <div className="text-center py-8">
            <p className="text-gray-500">데이터를 불러오는 중...</p>
          </div>
        )}
        
        {error && (
          <div className="text-center py-8">
            <p className="text-red-500">{error}</p>
          </div>
        )}
        
        {!isLoading && !error && chatData.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">신고 내역이 없습니다.</p>
          </div>
        )}
        
        {!isLoading && !error && chatData.length > 0 && (
          <>
            {/* 검색 결과 요약 */}
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex justify-between items-center">
                <p className="text-sm text-green-800">
                  총 <span className="font-medium">{chatData.length}</span>건의 신고 내역을 찾았습니다.
                  {(startDate || endDate) && (
                    <span className="ml-2 text-green-600">
                      (기간: {startDate ? new Date(startDate).toLocaleDateString('ko-KR') : '시작일'} ~ {endDate ? new Date(endDate).toLocaleDateString('ko-KR') : '종료일'})
                    </span>
                  )}
                </p>
                {(startDate || endDate) && (
                  <button
                    onClick={handleClearDateFilter}
                    className="text-xs text-green-600 hover:text-green-800 underline"
                  >
                    날짜 필터 초기화
                  </button>
                )}
              </div>
            </div>
            
            <DataTable columns={columns} data={chatData} />
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          </>
        )}
         {/* 피드백 모달 */}
        {isFeedbackModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
              {/* 모달 제목 동적 처리 */}
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">
                  {feedbackMode === "view"
                    ? (currentFeedback ? "검토 완료" : "검토 중")
                    : "피드백 작성"
                  }
                </h2>
                <button
                  onClick={handleCloseFeedbackModal}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              {feedbackMode === "view" ? (
                <div>
                  {currentFeedback ? (
                    <div>
                      <p className="text-gray-600 mb-4">피드백 내용:</p>
                      <div className="bg-gray-50 p-4 rounded-lg border">
                        <p className="whitespace-pre-wrap">{currentFeedback}</p>
                      </div>
                    </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500 text-lg">피드백을 입력해주세요.</p>
                    <p className="text-gray-500 text-sm mt-2">아직 검토가 진행 중입니다.</p>
                  </div>
                )}
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  피드백 작성
                </label>
                <textarea
                  value={feedbackContent}
                  onChange={(e) => setFeedbackContent(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="피드백 내용을 입력해주세요..."
                />
              </div>
            )}

            <div className="flex justify-end space-x-3 mt-6">
              {feedbackMode === "write" && (
                <button
                onClick={handleSaveFeedback}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500"
                >
                  저장
                </button>
              )}
              <button
                onClick={handleCloseFeedbackModal}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 focus:ring-2 focus:ring-gray-500"
                >
                  닫기
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatReportsPage;
