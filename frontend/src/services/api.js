import axios from "axios";
import { authService } from './authService';

// EC2 backend 서버 URL 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Axios 인스턴스 생성
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 요청 인터셉터
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 응답 인터셉터
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // 토큰 만료 시 리프레시 토큰으로 갱신 시도
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const response = await api.post('/auth/refresh/', {
                        refresh: refreshToken
                    });
                    
                    // 새로운 API 응답 구조에 맞게 수정
                    if (response.data.success && response.data.data) {
                        const newAccessToken = response.data.data.access_token;
                        localStorage.setItem('access_token', newAccessToken);
                        
                        // 원래 요청의 Authorization 헤더 업데이트
                        error.config.headers.Authorization = `Bearer ${newAccessToken}`;
                        
                        // 원래 요청 재시도
                        return api.request(error.config);
                    } else {
                        throw new Error('토큰 갱신 응답이 올바르지 않습니다.');
                    }
                } catch (refreshError) {
                    // 리프레시 실패 시 로그인 페이지로 이동
                    localStorage.clear();
                    window.location.href = '/login';
                }
            } else {
                // 리프레시 토큰이 없으면 로그인 페이지로 이동
                localStorage.clear();
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;