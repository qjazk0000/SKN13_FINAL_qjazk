
import { useNavigate } from "react-router-dom";
import { authService } from "../../../services/authService";


function AdminSidebar1({
  userName,
  selectedTab, 
  onTabSelect,
  onChatPageClick,
}) {
  const navigate = useNavigate();
  const initials = userName?.[0] || "A";
  const displayName = userName || "관리자";

  // 마이페이지 이동 핸들러
    const handleUserNameClick = () => {
      navigate("/chat");
    };
  
    // 로그아웃 핸들러
    const handleLogout = async () => {
      try {
        // 백엔드에 로그아웃 요청 (토큰 무효화)
        const response = await authService.logout();
  
        // 백엔드 응답 확인
        if (response && response.success) {
          console.log("백엔드 로그아웃 성공:", response.message);
        }
      } catch (error) {
        console.error("백엔드 로그아웃 실패:", error);
        // 백엔드 실패해도 계속 진행
      } finally {
        // 성공/실패와 관계없이 로컬 로그아웃 처리
        localStorage.clear();
  
        // 명시적으로 루트 페이지로만 이동 (로그인 화면)
        console.log("로그아웃 완료, 루트 페이지(/)로 이동");
        window.location.href = "/"; // 강제로 루트 페이지로 이동
      }
    };
  
    // 현재 선택된 탭에 따른 스타일 클래스 반환
    const getTabClass = (tabName) => {
      return selectedTab === tabName
        ? "bg-gray-700 text-white"
        : "text-gray-300 hover:bg-gray-700 hover:text-white";
    };

  return (
    <>
      <div className="flex flex-col w-72 h-screen bg-gray-800 text-white">
        {/* 상단 로고 */}
        <div
          className="flex items-center justify-center h-16 border-b border-gray-700 cursor-pointer"
          onClick={() => {
            sessionStorage.clear();
            window.location.reload();    
          }}
        >
          {/* <h1 className="text-xl font-bold">NAVI</h1> */}
          <img src="/images/logo3.png" alt="NAVI Logo" className="h-28 mr-3" />
        </div>

        {/* 카테고리 메뉴 */}
        <div className="flex flex-col px-2 py-4 gap-2">
          <div
            className={`flex items-center px-4 py-2 rounded-md cursor-pointer ${getTabClass(
              "회원 관리"
            )}`}
            onClick={() => onTabSelect("members")}
          >
            회원 관리
          </div>
          <div
            className={`flex items-center px-4 py-2 rounded-md cursor-pointer ${getTabClass(
              "채팅 신고 내역"
            )}`}
            onClick={() => onTabSelect("chat-reports")}
          >
            채팅 신고 내역
          </div>
          <div
            className={`flex items-center px-4 py-2 rounded-md cursor-pointer ${getTabClass(
              "영수증 관리"
            )}`}
            onClick={() => onTabSelect("manage-receipt")}
          >
            영수증 관리
          </div>
        </div>
          
        {/* 하단 사용자명 + 로그아웃 */}
        <div className="mt-auto px-4 py-3 border-t border-gray-700">
          <div className="mb-2">
            <button
              type="button"
              onClick={onChatPageClick}
              className="w-full py-1 px-4 text-white text-center font-medium underline hover:text-gray-400 transition"
              title="채팅 페이지로 이동"
            >
              채팅 페이지
            </button>
          </div>

          <div className="border-t border-gray-700 my-3"></div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 min-w-0">
              <div className="flex items-center justify-center h-8 w-8 rounded-full bg-gray-700 text-sm font-semibold">
                {initials}
              </div>
              <div className="min-w-0">
                <button
                  type="button"
                  onClick={handleUserNameClick}
                  className="text-m font-bold truncate hover:text-gray-400 transition cursor-pointer"
                  title="마이페이지로 이동"
                >
                  {displayName}
                </button>
              </div>
            </div>

            {/* 로그아웃 버튼 (inline SVG 아이콘) */}
            <button
              type="button"
              onClick={handleLogout}
              className="p-2 rounded-md hover:bg-gray-700 transition"
              aria-label="로그아웃"
              title="로그아웃"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M15 3h-6a2 2 0 0 0-2 2v4" />
                <path d="M7 15v4a2 2 0 0 0 2 2h6" />
                <path d="M10 12h9" />
                <path d="m18 15 3-3-3-3" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default AdminSidebar1;
