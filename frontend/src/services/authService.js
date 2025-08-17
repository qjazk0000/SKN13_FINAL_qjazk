import api from './api';

export const authService = {
    async login(userLoginId, password) {
        try {
            const response = await api.post('/auth/login/', {
                user_login_id: userLoginId,
                passwd: password,
            });

            if (response.data.token) {
                localStorage.setItem('access_token', response.data.token);
                localStorage.setItem('refresh_token', response.data.refresh);
                localStorage.setItem('user', response.data.user);
            }

            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.error || '로그인에 실패했습니다.');
        }
    },

    async logout(){
        try {
            await api.post('/auth/logout/');
        } finally {
            localStorage.clear();
        }
    },

    async checkAuthStatus() {
        try {
            // JWT 토큰이 있는지 확인
            const token = localStorage.getItem('access_token');
            if (!token) {
                return { status: 'unauthenticated' };
            }
            
            // 토큰 유효성 검증을 위해 사용자 프로필 요청
            const response = await api.get('/auth/profile/');
            return { status: 'authenticated', user: response.data };
        } catch (error) {
            if (error.response?.status === 401) {
                // 토큰이 만료되었거나 유효하지 않음
                localStorage.clear();
                return { status: 'unauthenticated' };
            }
            return { status: 'unauthenticated' };
        }
    },

    async refreshToken() {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) {
                throw new Error('리프레시 토큰이 없습니다.');
            }

            const response = await api.post('/auth/refresh/', {
                refresh: refreshToken
            });

            if (response.data.access) {
                localStorage.setItem('access_token', response.data.access);
                return response.data.access;
            }
        } catch (error) {
            localStorage.clear();
            throw new Error('토큰 갱신에 실패했습니다.');
        }
    },

    // 사용자 프로필 조회
    async getUserProfile() {
        try {
            const response = await api.get('/auth/profile/');
            
            if (response.data.success) {
                return response.data.data;  // 사용자 정보 반환
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            throw new Error('프로필 조회에 실패했습니다: ' + error.message);
        }
    },

    // 사용자 프로필 수정
    async updateUserProfile(userData) {
        try {
            const response = await api.put('/auth/profile/', userData);
            
            if (response.data.success) {
                return response.data.data;  // 업데이트된 사용자 정보 반환
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            throw new Error('프로필 수정에 실패했습니다: ' + error.message);
        }
    },

    // 비밀번호 변경
    async changePassword(passwordData) {
        try {
            const response = await api.post('/auth/password-change/', {
                current_password: passwordData.currentPassword,
                new_password: passwordData.newPassword,
                confirm_password: passwordData.confirmPassword
            });
            
            if (response.data.success) {
                return response.data.message;  // 성공 메시지 반환
            } else {
                throw new Error(response.data.message);
            }
        } catch (error) {
            throw new Error('비밀번호 변경에 실패했습니다: ' + error.message);
        }
    }
};