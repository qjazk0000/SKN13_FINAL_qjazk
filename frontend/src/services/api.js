import axios from "axios";

// 환경별 API URL 설정
const baseURL = process.env.REACT_APP_API_BASE_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://43.200.226.184' // Vercel에서 EC2 HTTPS 연결 (포트 443)
    : 'http://localhost:8000'); // 로컬 개발용

// Vercel 환경에서는 강제로 EC2 URL 사용
const isVercel = window.location.hostname.includes('vercel.app');
const finalBaseURL = isVercel ? 'https://43.200.226.184' : baseURL;

// 디버깅용 로그
console.log("Environment:", process.env.NODE_ENV);
console.log("Base URL:", baseURL);
console.log("Is Vercel:", isVercel);
console.log("Final Base URL:", finalBaseURL);
console.log("Final API URL:", `${finalBaseURL}/api`);

const api = axios.create({
  baseURL: `${finalBaseURL}/api`,
  withCredentials: true,
  timeout: 120000,
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // JWT 토큰이 있으면 헤더에 추가
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${token}`
      };
    }
    
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
    return response;
  },
  (error) => {
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
