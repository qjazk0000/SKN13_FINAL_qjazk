import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import dayjs from "dayjs";
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
  const [searchType, setSearchType] = useState("chat_id");

  const [members] = useState([
    {
      chat_id: "chat0101",
      dept: "개발팀",
      name: "김철수",
      rank: "사원",
      user_input: "추석 상여금 알려줘",
      llm_response: "추석 상여금에 대한 응답입니다.",
      chat_date: dayjs().format("YYYY-MM-DD HH:mm:ss"),
      error_type: "hallucination",
      reason: "추석 상여금 관련 없는 응답",
      reported_at: dayjs().format("YYYY-MM-DD HH:mm:ss"),
      remark: "검토 중"
    },
    {
      chat_id: "chat0102",
      dept: "영업팀",
      name: "이영희",
      rank: "대리",
      user_input: "연차 신청 방법",
      llm_response: "연차 신청 방법에 대한 응답입니다.",
      chat_date: dayjs().format("YYYY-MM-DD HH:mm:ss"),
      error_type: "incomplete",
      reason: "불완전 응답",
      reported_at: dayjs().format("YYYY-MM-DD HH:mm:ss"),
      remark: "처리완료"
    }
  ]);
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

  const fetchChatReports = async (page = 1) => {
    try {
      // 토큰 체크
      const token = localStorage.getItem("access_token");
      if (!token) {
        console.log("토큰이 없어 API 호출을 건너뜁니다.");
        return;
      }

      setIsLoading(true);
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

      if (searchTerm.trim()) {
        if (searchType === 'dept') {
          params.append("dept", searchTerm.trim());
        } else if (searchType === 'name') {
          params.append("name", searchTerm.trim());
        } else if (searchType === 'rank') {
          params.append("rank", searchTerm.trim());
        } else if (searchType === 'error_type') {
          params.append("error_type", searchTerm.trim());
        } 
      }
      
      const response = await api.get(`/admin/chat-reports/?${params.toString()}`);
      const data = response.data;
      if (data.success && data.data) {
        const chatReportsData = data.data.chat_reports || [];
        setChatData(chatReportsData);
        setTotalPages(data.data.total_pages);
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
  };

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
      accessor: "response",
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
      accessor: "error_reason",
      cell: (value) => value || "정보 없음"
    },
    {
      header: "신고 일시",
      accessor: "report_date",
      cell: (value) => {
        if (!value) return "정보 없음";
        const date = new Date(value);
        return date.toLocaleString('ko-KR'), {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        }
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
    { value: "remark", label: "처리 상태" }
  ];

  const handleDateChange = (start, end) => {
    setStartDate(start);
    setEndDate(end);
    fetchChatReports(1);
  };

   const handleSearch = () => {
    console.log(`검색 유형: ${searchType}, 검색어: ${searchTerm}`);
    setCurrentPage(1);
    fetchChatReports(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    // TODO: API 호출로 페이지 데이터 불러오기
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
         {/* 피드백 모달 */}
        {isFeedbackModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">
                  {feedbackMode === "view" ? "피드백 보기" : "피드백 작성"}
                </h2>
                <button
                  onClick={handleCloseFeedbackModal}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              {feedbackMode === "view" ? (
                // 피드백 보기 모드
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    피드백 내용
                  </label>
                  <div className="border border-gray-300 rounded-md p-3 bg-gray-50 min-h-[100px] whitespace-pre-wrap">
                    {currentFeedback}
                  </div>
                </div>
              ) : (
                // 피드백 작성 모드
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    피드백 작성
                  </label>
                  <textarea
                    value={feedbackContent}
                    onChange={(e) => setFeedbackContent(e.target.value)}
                    className="w-full border border-gray-300 rounded-md p-3 min-h-[100px] resize-none"
                    placeholder="피드백 내용을 입력해주세요..."
                  />
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <button
                  onClick={handleCloseFeedbackModal}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  닫기
                </button>
                {feedbackMode === "write" && (
                  <button
                    onClick={handleSaveFeedback}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    저장
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatReportsPage;
