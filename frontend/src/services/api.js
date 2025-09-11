import axios from "axios";

// 환경별 API URL 설정
const baseURL = process.env.NODE_ENV === 'production' 
  ? '' // Vercel에서 같은 도메인 사용 (Serverless Function)
  : 'http://localhost:8000'; // 로컬 개발용

// Vercel 배포 환경에서는 항상 Serverless Function 사용
const isVercelDeployment = window.location.hostname.includes('vercel.app');
const finalBaseURL = isVercelDeployment ? '' : baseURL;

// 디버깅용 로그
console.log("Environment:", process.env.NODE_ENV);
console.log("Base URL:", baseURL);
console.log("Is Vercel Deployment:", isVercelDeployment);
console.log("Final Base URL:", finalBaseURL);
console.log("Final API URL:", finalBaseURL ? `${finalBaseURL}/api` : '/api');

const api = axios.create({
  baseURL: finalBaseURL ? `${finalBaseURL}/api` : '/api', // Vercel에서는 상대 경로 사용
  withCredentials: true,
  timeout: 120000,
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 디버깅용 로그
    console.log("API 요청:", config.method?.toUpperCase(), config.url);
    console.log("Full URL:", config.baseURL + config.url);
    
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
