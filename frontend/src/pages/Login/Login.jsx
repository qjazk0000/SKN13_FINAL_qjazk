import React, { useState } from "react";
import { authService } from "../../services/authService";

function Login() {
  const [userLoginId, setUserLoginId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await authService.login(userLoginId, password);
      alert("로그인 되었습니다.");
      window.location.href = "/chat"; // 로그인 성공 후 채팅 페이지로 이동
    } catch (err) {
      setError(err.message || "아이디 또는 비밀번호가 올바르지 않습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="bg-white dark:bg-gray-800 p-10 rounded-xl shadow-lg w-full max-w-md transition-colors duration-300">
        {/* NAVI 로고 추가 */}
        <div className="flex flex-col items-center mb-2">
          <img
            src="/images/NAVI.png"
            alt="NAVI Logo"
            className="w-28 h-auto mb-4"
          />
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <input
              className="w-full p-4 border border-gray-300 dark:border-gray-600 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-gray-50 dark:bg-gray-700 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200"
              type="text"
              placeholder="사용자명"
              value={userLoginId}
              onChange={(e) => setUserLoginId(e.target.value)}
              required
            />
          </div>
          <div className="mb-6">
            <input
              className="w-full p-4 border border-gray-300 dark:border-gray-600 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-gray-50 dark:bg-gray-700 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200"
              type="password"
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && (
            <p className="text-red-500 text-center mb-4 text-sm">{error}</p>
          )}
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full p-4 mt-2 bg-orange-300 text-white font-bold text-lg rounded-lg shadow-lg transition-colors duration-200 ${
              isLoading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "hover:bg-orange-400"
            }`}
          >
            {isLoading ? "로그인 중..." : "로그인"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
