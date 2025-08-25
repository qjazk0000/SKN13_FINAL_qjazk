import axios from "axios";
import { authService } from "./authService";
// EC2 backend 서버 URL 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';
// Axios 인스턴스 생성
// const api = axios.create({
//     baseURL: API_BASE_URL,
//     headers: {
//         'Content-Type': 'application/json',
//     },
/**
 * 프론트는 3000에서 돌더라도, API는 Nginx(80)로 고정 라우팅
 * - dev/localhost: http://localhost/api
 * - prod/vercel 등: 환경변수 REACT_APP_API_BASE_URL 사용 가능
 */
const baseURL =
  process.env.REACT_APP_API_BASE_URL?.replace(/\/$/, "") || "http://localhost"; // 끝 슬래시 제거된 형태

const api = axios.create({
  baseURL: `${baseURL}/api`,
  withCredentials: true,
  timeout: 20000,
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log(
      "API 요청 인터셉터 실행:",
      config.method?.toUpperCase(),
      config.url
    );
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.log("토큰이 없음");
    }
    console.log("최종 요청 설정:", config);
    return config;
  },
  (error) => {
    console.error("요청 인터셉터 에러:", error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 단순화
api.interceptors.response.use(
  (response) => {
    console.log(
      "API 응답 성공:",
      response.config.method?.toUpperCase(),
      response.config.url,
      response.status
    );
    return response;
  },
  async (error) => {
    console.error(
      "API 응답 에러:",
      error.config?.method?.toUpperCase(),
      error.config?.url,
      error.response?.status
    );
    if (error.response?.status === 401) {
      // 401 에러는 authService에서 처리하도록 그대로 전달
      console.log("401 에러 발생, authService에서 처리");
    }
    return Promise.reject(error);
  }
);

export default api;
