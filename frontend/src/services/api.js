// src/api.js
import axios from "axios";

// 환경별 API ORIGIN (도메인까지만)
// prod 기본값은 https://api.growing.ai.kr
const originFromEnv =
  process.env.REACT_APP_API_BASE_URL ||
  (process.env.NODE_ENV === "production"
    ? "https://api.growing.ai.kr"
    : "http://localhost:8000");

// 혹시 모를 끝 슬래시 제거 (//api 방지)
const ORIGIN = originFromEnv.replace(/\/+$/, "");

// 디버깅용 로그
console.log("Environment:", process.env.NODE_ENV);
console.log("Base URL:", ORIGIN);

// ⚠️ 여기서 /api를 '한 번만' 붙입니다.
const api = axios.create({
  baseURL: `${ORIGIN}/api`,
  withCredentials: true,
  timeout: 120000,
});

// 요청 인터셉터: JWT 있으면 Authorization 부착
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 응답 인터셉터(필요 시 커스터마이즈)
api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error)
);

export default api;
