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

    async checkAuthStatus() {
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

    async refreshToken() {
        try {
            console.log('토큰 갱신 시작...');
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) {
                throw new Error('리프레시 토큰이 없습니다.');
            }

            console.log('리프레시 토큰으로 갱신 요청...');
            const response = await api.post('/auth/refresh/', {
                refresh: refreshToken
            });

            console.log('토큰 갱신 응답:', response.data);

            if (response.data.success && response.data.data) {
                const newAccessToken = response.data.data.access_token;
                localStorage.setItem('access_token', newAccessToken);
                console.log('새로운 액세스 토큰 저장 완료');
                return newAccessToken;
            } else {
                throw new Error('토큰 갱신 응답이 올바르지 않습니다.');
            }
        } catch (error) {
            console.error('토큰 갱신 실패:', error);
            // 토큰 갱신 실패 시 로컬 스토리지 클리어
            localStorage.clear();
            throw new Error('토큰 갱신에 실패했습니다.');
        }
    },

    // 사용자 프로필 조회
    async getUserProfile() {
        try {
            console.log('프로필 조회 시작...');
            
            // 토큰 재확인
            const token = localStorage.getItem('access_token');
            console.log('프로필 조회 시 토큰 상태:', token ? '존재' : '없음');
            
            if (!token) {
                throw new Error('액세스 토큰이 없습니다.');
            }
            
            const response = await api.get('/auth/profile/');
            console.log('프로필 조회 응답:', response.data);
            console.log('응답 상태:', response.status);
            
            if (response.data.success) {
                console.log('프로필 조회 성공, 데이터:', response.data.data);
                return response.data.data;  // 사용자 정보 반환
            } else {
                console.log('프로필 조회 실패, 메시지:', response.data.message);
                throw new Error(response.data.message || '프로필 조회 실패');
            }
        } catch (error) {
            console.error('프로필 조회 에러 상세:', error);
            console.error('에러 응답:', error.response);
            console.error('에러 상태:', error.response?.status);
            
            // 401 에러인 경우 토큰 갱신 시도
            if (error.response?.status === 401) {
                console.log('401 에러 발생, 토큰 갱신 시도...');
                try {
                    const newToken = await this.refreshToken();
                    console.log('토큰 갱신 성공, 프로필 재조회 시도...');
                    
                    // 새로운 토큰으로 프로필 재조회
                    const retryResponse = await api.get('/auth/profile/');
                    if (retryResponse.data.success) {
                        console.log('토큰 갱신 후 프로필 조회 성공');
                        return retryResponse.data.data;
                    } else {
                        throw new Error('토큰 갱신 후에도 프로필 조회 실패');
                    }
                } catch (refreshError) {
                    console.error('토큰 갱신 실패:', refreshError);
                    // 토큰 갱신 실패 시 원본 에러를 던짐
                    throw error;
                }
            }
            
            // 원본 에러 정보를 유지하면서 던지기
            if (error.response) {
                // 서버 응답이 있는 경우
                console.log('서버 응답 에러:', error.response.status, error.response.data);
                throw error;
            } else if (error.request) {
                // 요청은 보냈지만 응답을 받지 못한 경우
                console.log('요청은 보냈지만 응답 없음');
                throw new Error('서버에 연결할 수 없습니다.');
            } else {
                // 그 외 에러
                console.log('기타 에러:', error.message);
                throw error;
            }
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
    },

    // 현재 로그인한 사용자 정보 가져오기
    getCurrentUser() {
        try {
            const userStr = localStorage.getItem('user');
            return userStr ? JSON.parse(userStr) : null;
        } catch (error) {
            console.error('사용자 정보 파싱 오류:', error);
            return null;
        }
    },

    // 사용자 정보 업데이트 (로컬 스토리지)
    updateCurrentUser(userData) {
        try {
            localStorage.setItem('user', JSON.stringify(userData));
        } catch (error) {
            console.error('사용자 정보 저장 오류:', error);
        }
    }
};