import axios from "axios";

const baseURL =
  process.env.REACT_APP_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

const api = axios.create({
  baseURL: `${baseURL}/api`,
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
