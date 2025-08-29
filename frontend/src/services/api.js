import axios from "axios";
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
  process.env.REACT_APP_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000"; // Django 개발 서버 포트로 수정

const api = axios.create({
  baseURL: `${baseURL}/api`,
  withCredentials: true,
  timeout: 120000, // RAG 시스템 처리 시간을 고려하여 120초로 증가
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log("API 요청 인터셉터 실행:", config.method?.toUpperCase(), config.url);
    
    // JWT 토큰이 있으면 헤더에 추가
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    console.log("최종 요청 설정:", config);
    return config;
  },
  (error) => {
    console.error("API 요청 인터셉터 오류:", error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    console.log("API 응답 성공:", response.config.method?.toUpperCase(), response.config.url, response.status);
    return response;
  },
  (error) => {
    console.log("API 응답 에러:", error.config?.method?.toUpperCase(), error.config?.url, error.response?.status);
    
    // 401 에러는 그대로 전달 (리다이렉트 없음)
    // if (error.response?.status === 401) {
    //   localStorage.removeItem("access_token");
    //   localStorage.removeItem("refresh_token");
    //   localStorage.removeItem("user");
    //   window.location.href = "/login";
    // }
    
    return Promise.reject(error);
  }
);

export default api;
