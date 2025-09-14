import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import AdminSidebar from "./components/AdminSidebar.jsx";
import SearchBar from "./components/SearchBar";
// DataTable는 카드 UI로 대체됩니다
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
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // 날짜 필터 상태
  // UI 선택값 
  const [selectedStartDate, setSelectedStartDate] = useState("");
  const [selectedEndDate, setSelectedEndDate] = useState("");
  // 실제 검색에 적용될 값 
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
  // useEffect(() => {
  //   // 날짜가 변경되었을 때만 실행
  //   if (startDate || endDate) {
  //     // 약간의 지연을 두어 상태 업데이트가 완료된 후 검색 실행
  //     const timer = setTimeout(async () => {
  //       try {
  //         // 데이터를 미리 로드
  //         const params = new URLSearchParams();
  //         params.append("page", "1");
  //         params.append("page_size", "8");

  //         if (startDate) {
  //           params.append("start_date", startDate);
  //         }
  //         if (endDate) {
  //           params.append("end_date", endDate);
  //         }

  //         // 검색 조건 처리
  //         const trimmedSearchTerm = searchTerm.trim();
  //         if (trimmedSearchTerm) {
  //           if (searchType === "dept") {
  //             params.append("dept", trimmedSearchTerm);
  //           } else if (searchType === "name") {
  //             params.append("name", trimmedSearchTerm);
  //           } else if (searchType === "rank") {
  //             params.append("rank", trimmedSearchTerm);
  //           } else if (searchType === "error_type") {
  //             params.append("error_type", trimmedSearchTerm);
  //           } else if (searchType === "reason") {
  //             params.append("reason", trimmedSearchTerm);
  //           } else if (searchType === "remark") {
  //             params.append("remark", trimmedSearchTerm);
  //           }
  //         }

  //         const response = await api.get(
  //           `/admin/conversations/reports/?${params.toString()}`
  //         );

  //         if (response.data.success) {
  //           // 깜빡임 완전 방지: React 18의 배치 업데이트 활용
  //           React.startTransition(() => {
  //             setChatData(response.data.data.reports);
  //             setTotalPages(response.data.data.total_pages);
  //             setTotalCount(response.data.data.total_count || 0);
  //             setCurrentPage(1);
  //           });
  //         }
  //       } catch (error) {
  //         console.error("날짜 필터 검색 실패:", error);
  //       }
  //     }, 100);

  //     return () => clearTimeout(timer);
  //   }
  // }, [startDate, endDate, searchTerm, searchType]); // eslint-disable-line react-hooks/exhaustive-deps

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

  const fetchChatReports = useCallback(
    async (page = 1, showLoading = true, filters = {}) => {
        const s = filters.startDate ?? startDate;
        const e = filters.endDate ?? endDate;
      try {
        // 토큰 체크
        const token = localStorage.getItem("access_token");
        if (!token) {
          console.log("토큰이 없어 API 호출을 건너뜁니다.");
          return;
        }

        if (showLoading) {
          setIsLoading(true);
        }
        setError("");

        const params = new URLSearchParams();
        params.append("page", page.toString());
        params.append("page_size", "8");

        if (s) {params.append("start_date", s);}
        if (e) {params.append("end_date", e);}

        // 검색 조건 처리
        const trimmedSearchTerm = searchTerm.trim();

        if (trimmedSearchTerm) {
          if (searchType === "dept") {
            params.append("dept", trimmedSearchTerm);
          } else if (searchType === "name") {
            params.append("name", trimmedSearchTerm);
          } else if (searchType === "rank") {
            params.append("rank", trimmedSearchTerm);
          } else if (searchType === "error_type") {
            params.append("error_type", trimmedSearchTerm);
          } else if (searchType === "reason") {
            params.append("reason", trimmedSearchTerm);
          } else if (searchType === "remark") {
            params.append("remark", trimmedSearchTerm);
          }
        }

        const response = await api.get(
          `/admin/conversations/reports/?${params.toString()}`
        );

        if (response.data.success) {
          // 백엔드 검색 결과 사용
          setChatData(response.data.data.reports);
          setTotalPages(response.data.data.total_pages);
          setTotalCount(response.data.data.total_count || 0);
          setCurrentPage(page);
        } else {
          throw new Error(response.data.message || "API 응답 오류");
        }
      } catch (error) {
        console.error("채팅 신고 데이터 로드 실패:", error);
        setError("채팅 신고 데이터 로드 실패");
      } finally {
        setIsLoading(false);
      }
    },
    [startDate, endDate, searchTerm, searchType]
  );

  useEffect(() => {
    // 검색 조건이 모두 초기화된 경우에만 fetch 수행
    if (
      searchTerm === "" &&
      startDate === "" &&
      endDate === "" &&
      currentPage === 1
    ) {
      fetchChatReports(1);
    }
  }, [searchTerm, startDate, endDate, currentPage, fetchChatReports]);

  // 테이블 컬럼은 카드 UI로 대체

  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [feedbackContent, setFeedbackContent] = useState("");
  const [feedbackMode, setFeedbackMode] = useState("");
  const [currentFeedback, setCurrentFeedback] = useState("");
  const [selectedReport, setSelectedReport] = useState(null);
  const [adminErrorType, setAdminErrorType] = useState("");

  // 피드백 보기/작성 핸들러는 카드 클릭으로 통합됨

  // 카드 클릭 시 상세 보기 모달 오픈
  const openReportDetail = (report) => {
    setSelectedReport(report);
    setSelectedChatId(report?.chat_id || report?.id || null);
    setAdminErrorType(report?.error_type || "");
    const remark = (report?.remark || "").trim();
    if (remark) {
      setCurrentFeedback(remark);
      setFeedbackMode("view");
    } else {
      setCurrentFeedback("");
      setFeedbackContent("");
      setFeedbackMode("write");
    }
    setIsFeedbackModalOpen(true);
  };

  const handleSaveFeedback = async () => {
    try {
      if (!feedbackContent.trim()) {
        alert("피드백 내용을 입력해주세요.");
        return;
      }

      if (!adminErrorType) {
        alert("관리자 판단 신고 유형을 선택해주세요.");
        return;
      }

      const response = await api.post(
        `/admin/chat-reports/${selectedChatId}/feedback/`,
        {
          remark: feedbackContent.trim(),
          admin_error_type: adminErrorType,
        }
      );

      if (response.data.success) {
        alert("피드백이 성공적으로 저장되었습니다.");
        setIsFeedbackModalOpen(false);

        // 해당 카드의 데이터만 업데이트
        setChatData((prevData) =>
          prevData.map((report) =>
            report.chat_id === selectedChatId
              ? {
                  ...report,
                  error_type: adminErrorType,
                  remark: feedbackContent.trim(),
                }
              : report
          )
        );
      } else {
        alert("피드백 저장에 실패했습니다.");
      }
    } catch (error) {
      console.error("피드백 저장 실패:", error);
      alert("피드백 저장 중 오류가 발생했습니다.");
    }
  };

  const handleEditFeedback = () => {
    setFeedbackContent(currentFeedback);
    setFeedbackMode("write");
  };

  const handleEditErrorType = () => {
    setFeedbackMode("write");
  };

  // 피드백 모달 달기
  const handleCloseFeedbackModal = () => {
    setIsFeedbackModalOpen(false);
    setSelectedChatId(null);
    setFeedbackContent("");
    setCurrentFeedback("");
    setFeedbackMode("");
    setAdminErrorType("");
    setSelectedReport(null);
  };

  const searchOptions = [
    { value: "dept", label: "부서명" },
    { value: "name", label: "이름" },
    { value: "rank", label: "직급" },
    { value: "error_type", label: "신고 유형" },
    { value: "remark", label: "비고" },
  ];

  // 신고 유형 선택 옵션 (한국어)
  const errorTypeOptions = [
    { value: "불완전", label: "불완전" },
    { value: "환각", label: "환각" },
    { value: "사실 오류", label: "사실 오류" },
    { value: "무관련", label: "무관련" },
    { value: "기타", label: "기타" },
  ];

  const handleDateChange = (start, end) => {
    // 날짜 유효성 검사
    if (start && end && start > end) {
      alert("시작일은 종료일보다 이전이어야 합니다.");
      return;
    }

    setSelectedStartDate(start);
    setSelectedEndDate(end);
    // 날짜 변경 시 1페이지부터 검색 시작
    setCurrentPage(1);
    // fetchChatReports(1);
  };

  const handleSearch = () => {
    // 검색어가 없어도 날짜 필터가 있으면 검색 가능
    // if (!searchTerm.trim() && !startDate && !endDate) {
    //   alert("검색어 또는 날짜를 입력해주세요.");
    //   return;
    // }
    setStartDate(selectedStartDate);
    setEndDate(selectedEndDate); 
    setCurrentPage(1);
    fetchChatReports(1, true, {startDate:selectedStartDate, endDate:selectedEndDate});
  };

  const handleClearSearch = () => {
    setSearchTerm("");
    setSearchType("dept");
    setStartDate("");
    setEndDate("");
    setSelectedStartDate("");
    setSelectedEndDate("");
    setCurrentPage(1);
    // 검색 조건 초기화 시 데이터도 전체 목록으로 갱신
    fetchChatReports(1, true, { startDate: "", endDate: "" });
  };

  // 날짜 필터만 초기화
  // const handleClearDateFilter = async () => {
  //   setStartDate("");
  //   setEndDate("");
  //   setCurrentPage(1);
  //   // fetchChatReports(1);
  //   console.log("날짜 필터가 초기화되었습니다.", startDate, endDate);
  // };

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
    <div className="flex h-screen">
      <div className="w-72 bg-gray-800 text-white flex-shrink-0 h-screen">
        <AdminSidebar
          userName={userName}
          selectedTab={selectedTab}
          onTabSelect={handleTabSelect}
          onChatPageClick={handleChatPageClick}
        />
      </div>
      <div className="flex-1 overflow-y-auto p-6 bg-white">
        <h1 className="text-2xl font-bold mb-6">채팅 신고 내역</h1>
        <div className="mb-2">
          <DateSelectBar
            startDate={selectedStartDate}
            endDate={selectedEndDate}
            onDateChange={handleDateChange}
            // onClearDateFilter={handleClearDateFilter}
          />
        </div>

        <div className="mb-2">
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
        </div>

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
                  총 <span className="font-medium">{totalCount}</span>건의 신고
                  내역을 찾았습니다.
                  {(startDate || endDate) && (
                    <span className="ml-2 text-green-600">
                      (기간:{" "}
                      {startDate
                        ? new Date(startDate).toLocaleDateString("ko-KR")
                        : "시작일"}{" "}
                      ~{" "}
                      {endDate
                        ? new Date(endDate).toLocaleDateString("ko-KR")
                        : "종료일"}
                      )
                    </span>
                  )}
                </p>
                {(startDate || endDate) && (
                  <button
                    // onClick={handleClearDateFilter}
                    className="text-xs text-green-600 hover:text-green-800 underline"
                  >
                    날짜 필터 초기화
                  </button>
                )}
              </div>
            </div>

            {/* 카드 그리드 렌더링 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {chatData.map((report, index) => {
                const errorTypeMap = {
                  hallucination: "환각",
                  fact_error: "사실 오류",
                  irrelevant: "관련 없음",
                  incomplete: "불완전",
                  other: "기타",
                };
                const errorTypeKr =
                  errorTypeMap[report?.error_type] ||
                  report?.error_type ||
                  "정보 없음";
                const reportedAtText = report?.reported_at
                  ? new Date(report.reported_at).toLocaleString("ko-KR", {
                      year: "numeric",
                      month: "2-digit",
                      day: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : "정보 없음";

                return (
                  <div
                    key={`${
                      report.report_id || report.chat_id || "unknown"
                    }-${index}-${report.reported_at || Date.now()}`}
                    className="cursor-pointer rounded-xl border border-gray-200 bg-white p-4 shadow hover:shadow-md transition"
                    onClick={() => openReportDetail(report)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="text-sm text-gray-500">
                        {reportedAtText}
                      </div>
                      <span
                        className={`inline-block rounded-full px-2 py-0.5 text-xs ${
                          report?.remark && report.remark.trim()
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                        }`}
                      >
                        {errorTypeKr}
                      </span>
                    </div>
                    <div className="mt-3 space-y-1">
                      <div className="text-sm">
                        <span className="text-gray-500">부서: </span>
                        <span className="font-medium">
                          {report?.dept || "정보 없음"}
                        </span>
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-500">직급: </span>
                        <span className="font-medium">
                          {report?.rank || "정보 없음"}
                        </span>
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-500">이름: </span>
                        <span className="font-medium">
                          {report?.name || "정보 없음"}
                        </span>
                      </div>
                      <div className="text-sm">
                        <span className="text-gray-500">신고 사유: </span>
                        <span className="font-medium line-clamp-2">
                          {report?.reason || "정보 없음"}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
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
            <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[85vh] overflow-y-auto">
              {/* 모달 제목 동적 처리 */}
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">
                  {feedbackMode === "view"
                    ? currentFeedback
                      ? "검토 완료"
                      : "검토 중"
                    : "피드백 작성"}
                </h2>
                <button
                  onClick={handleCloseFeedbackModal}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              {/* 상세 정보 섹션: 요약 + 본문 + 피드백 */}
              <div className="space-y-6">
                {/* 요약 정보 카드 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="rounded-lg border p-4">
                    <div className="text-sm text-gray-500">부서</div>
                    <div className="font-medium">
                      {selectedReport?.dept || "정보 없음"}
                    </div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <div className="text-sm text-gray-500">직급</div>
                    <div className="font-medium">
                      {selectedReport?.rank || "정보 없음"}
                    </div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <div className="text-sm text-gray-500">이름</div>
                    <div className="font-medium">
                      {selectedReport?.name || "정보 없음"}
                    </div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <div className="text-sm text-gray-500">신고 일시</div>
                    <div className="font-medium">
                      {selectedReport?.reported_at
                        ? new Date(selectedReport.reported_at).toLocaleString(
                            "ko-KR",
                            {
                              year: "numeric",
                              month: "2-digit",
                              day: "2-digit",
                              hour: "2-digit",
                              minute: "2-digit",
                            }
                          )
                        : "정보 없음"}
                    </div>
                  </div>

                  {/* 신고 유형 비교 섹션 */}
                  <div className="rounded-lg border p-4">
                    <div className="text-sm text-gray-500 mb-2">
                      사용자 신고 유형
                    </div>
                    <div className="font-medium text-gray-800">
                      {(() => {
                        const map = {
                          hallucination: "환각",
                          fact_error: "사실 오류",
                          irrelevant: "관련 없음",
                          incomplete: "불완전",
                          other: "기타",
                        };
                        return (
                          map[selectedReport?.error_type] ||
                          selectedReport?.error_type ||
                          "정보 없음"
                        );
                      })()}
                    </div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="text-sm text-gray-500">
                        관리자 판단 신고 유형
                      </div>
                      {feedbackMode === "view" && selectedReport?.remark && (
                        <button
                          onClick={handleEditErrorType}
                          className="text-xs text-blue-600 hover:text-blue-800 underline"
                        >
                          수정
                        </button>
                      )}
                    </div>
                    <div className="font-medium text-blue-600">
                      {(() => {
                        const map = {
                          hallucination: "환각",
                          fact_error: "사실 오류",
                          irrelevant: "관련 없음",
                          incomplete: "불완전",
                          other: "기타",
                        };
                        return (
                          map[selectedReport?.error_type] ||
                          selectedReport?.error_type ||
                          "정보 없음"
                        );
                      })()}
                    </div>
                  </div>

                  <div className="rounded-lg border p-4 md:col-span-2">
                    <div className="text-sm text-gray-500">
                      사용자 신고 사유
                    </div>
                    <div className="font-medium whitespace-pre-wrap">
                      {selectedReport?.reason || "정보 없음"}
                    </div>
                  </div>
                  {selectedReport?.remark && (
                    <div className="rounded-lg border p-4 md:col-span-2">
                      <div className="text-sm text-gray-500">
                        관리자 판단 사유
                      </div>
                      <div className="font-medium text-blue-600 whitespace-pre-wrap">
                        {selectedReport?.remark || "정보 없음"}
                      </div>
                    </div>
                  )}
                </div>

                {/* 본문: 사용자 입력 / LLM 응답 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="rounded-lg border p-4">
                    <div className="text-sm font-semibold text-gray-700 mb-2">
                      사용자 입력
                    </div>
                    <div className="whitespace-pre-wrap text-gray-800 min-h-[80px]">
                      {selectedReport?.user_input || "정보 없음"}
                    </div>
                  </div>
                  <div className="rounded-lg border p-4">
                    <div className="text-sm font-semibold text-gray-700 mb-2">
                      LLM 응답
                    </div>
                    <div className="prose prose-sm max-w-none min-h-[80px]">
                      <ReactMarkdown>
                        {selectedReport?.llm_response || "정보 없음"}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>

                {/* 관리자 판단 신고 유형 선택 */}
                {feedbackMode === "write" && (
                  <div className="rounded-lg border p-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      관리자 판단 신고 유형 *
                    </label>
                    <select
                      value={adminErrorType}
                      onChange={(e) => setAdminErrorType(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">신고 유형을 선택하세요</option>
                      <option value="hallucination">환각</option>
                      <option value="fact_error">사실 오류</option>
                      <option value="irrelevant">관련 없음</option>
                      <option value="incomplete">불완전</option>
                      <option value="other">기타</option>
                    </select>
                  </div>
                )}

                {/* 피드백 */}
                {feedbackMode === "view" ? (
                  <div className="rounded-lg border p-4">
                    {currentFeedback ? (
                      <>
                        <div className="flex justify-between items-center mb-2">
                          <div className="text-sm font-semibold text-gray-700">
                            피드백
                          </div>
                          <button
                            onClick={handleEditFeedback}
                            className="text-sm text-blue-600 hover:text-blue-800 underline"
                          >
                            수정
                          </button>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg border whitespace-pre-wrap">
                          {currentFeedback}
                        </div>
                      </>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-gray-500 text-lg">
                          피드백을 입력해주세요.
                        </p>
                        <p className="text-gray-500 text-sm mt-2">
                          아직 검토가 진행 중입니다.
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="rounded-lg border p-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      피드백 작성
                    </label>
                    <textarea
                      value={feedbackContent}
                      onChange={(e) => setFeedbackContent(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[120px]"
                      placeholder="피드백 내용을 입력해주세요..."
                    />
                  </div>
                )}
              </div>

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
