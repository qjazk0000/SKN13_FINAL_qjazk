import api from './api';

export const authService = {
    async login(userLoginId, password) {
        try {
            const response = await api.post('/auth/login/', {
                user_login_id: userLoginId,
                passwd: password,
            });

            if (response.data.success && response.data.data) {
                // 새로운 API 응답 구조에 맞게 수정
                localStorage.setItem('access_token', response.data.data.access_token);
                localStorage.setItem('refresh_token', response.data.data.refresh_token);
                localStorage.setItem('user', JSON.stringify(response.data.data.user));
            }

            return response.data;
        } catch (error) {
            throw new Error(error.response?.data?.message || '로그인에 실패했습니다.');
        }
    },

    async logout(){
        try {
            const response = await api.post('/auth/logout/');
            return response.data;  // 응답 데이터 반환
        } catch (error) {
            console.error('로그아웃 API 오류:', error);
            throw error;  // 에러를 다시 던져서 상위에서 처리
        } finally {
            localStorage.clear();
        }
    },

    async checkAuthStatus() {  // 로그인 상태 확인인
        try {
            // JWT 토큰이 있는지 확인
            const token = localStorage.getItem('access_token');
            if (!token) {
                return { status: 'unauthenticated' };
            }
            
            // 토큰 유효성 검증을 위해 사용자 프로필 요청
            const response = await api.get('/auth/profile/');
            if (response.data.success) {
                return { status: 'authenticated', user: response.data.data };
            } else {
                return { status: 'unauthenticated' };
            }
        } catch (error) {
            if (error.response?.status === 401) {
                // 토큰이 만료되었거나 유효하지 않음
                localStorage.clear();
                return { status: 'unauthenticated' };
            }
            return { status: 'unauthenticated' };
        }
    },

    async refreshToken() {  // 토큰 갱신
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) {
                throw new Error('리프레시 토큰이 없습니다.');
            }

            const response = await api.post('/auth/refresh/', {
                refresh: refreshToken
            });

            if (response.data.success && response.data.data) {
                const newAccessToken = response.data.data.access_token;
                localStorage.setItem('access_token', newAccessToken);
                return newAccessToken;
            } else {
                throw new Error('토큰 갱신 응답이 올바르지 않습니다.');
            }
        } catch (error) {
            localStorage.clear();
            throw new Error('토큰 갱신에 실패했습니다.');
        }
    },

    // 사용자 프로필 조회
    async getUserProfile() {  // 사용자 프로필 조회
        try {
            const response = await api.get('/auth/profile/');
            
            if (response.data.success) {
                return response.data.data;  // 사용자 정보 반환
                throw new Error(response.data.message);
            }
        } catch (error) {
            throw new Error('프로필 조회에 실패했습니다: ' + error.message);
        }
    },

    // 사용자 프로필 수정
    async updateUserProfile(userData) {  // 사용자 프로필 수정
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
    async changePassword(passwordData) {  // 비밀번호 변경
        try {
            const response = await api.post('/user/password-change/', {
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
    },

    // 로그인 후 유저 정보 표시시
    getCurrentUser() {  // 현재 로그인한 사용자 정보 가져오기
        try {
            const userStr = localStorage.getItem('user');
            return userStr ? JSON.parse(userStr) : null;
        } catch (error) {
            console.error('사용자 정보 파싱 오류:', error);
            return null;
        }
    },

    // 관리자 여부 확인
    isAdmin() {
        try {
            const user = this.getCurrentUser();
            return user && user.auth === 'Y';
        } catch (error) {
            console.error('관리자 여부 확인 오류:', error);
            return false;
        }
    },

    // JWT 토큰 가져오기
    getToken() {
        return localStorage.getItem('access_token');
    },


    updateCurrentUser(userData) {  // 사용자 정보 업데이트 (로컬 스토리지)
        try {
            localStorage.setItem('user', JSON.stringify(userData));
        } catch (error) {
            console.error('사용자 정보 저장 오류:', error);
        }

    }
};