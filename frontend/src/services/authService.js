// authService.js
import api from './api';

const pickErrorMessage = (error) =>
  error?.response?.data?.message ||
  error?.response?.data?.detail ||
  (typeof error?.response?.data === 'string' ? error.response.data : '') ||
  error?.message ||
  '요청 처리에 실패했습니다.';

export const authService = {
  async login(userLoginId, password) {
    try {
      const res = await api.post('/api/auth/login/', {
        user_login_id: userLoginId,
        passwd: password,
      });

      if (res.data?.success && res.data?.data) {
        localStorage.setItem('access_token', res.data.data.access_token);
        localStorage.setItem('refresh_token', res.data.data.refresh_token);
        localStorage.setItem('user', JSON.stringify(res.data.data.user));
      }
      return res.data;
    } catch (err) {
      throw new Error(pickErrorMessage(err) || '로그인에 실패했습니다.');
    }
  },

  async logout() {
    try {
      const res = await api.post('/api/auth/logout/');
      return res.data;
    } catch (err) {
      console.error('로그아웃 API 오류:', err);
      throw new Error(pickErrorMessage(err) || '로그아웃에 실패했습니다.');
    } finally {
      localStorage.clear();
    }
  },

  async checkAuthStatus() {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return { status: 'unauthenticated' };

      const res = await api.get('/api/auth/profile/');
      return res.data?.success
        ? { status: 'authenticated', user: res.data.data }
        : { status: 'unauthenticated' };
    } catch (err) {
      if (err.response?.status === 401) localStorage.clear();
      return { status: 'unauthenticated' };
    }
  },

  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) throw new Error('리프레시 토큰이 없습니다.');

      const res = await api.post('/api/auth/refresh/', { refresh: refreshToken });
      if (res.data?.success && res.data?.data) {
        const newAccessToken = res.data.data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        return newAccessToken;
      }
      throw new Error('토큰 갱신 응답이 올바르지 않습니다.');
    } catch (err) {
      localStorage.clear();
      throw new Error(pickErrorMessage(err) || '토큰 갱신에 실패했습니다.');
    }
  },

  async getUserProfile() {
    try {
      const res = await api.get('/api/auth/profile/');
      if (res.data?.success) return res.data.data;
      throw new Error(res.data?.message || '프로필 조회 실패');
    } catch (err) {
      throw new Error('프로필 조회에 실패했습니다: ' + pickErrorMessage(err));
    }
  },

  async updateUserProfile(userData) {
    try {
      const res = await api.put('/api/auth/profile/', userData);
      if (res.data?.success) return res.data.data;
      throw new Error(res.data?.message || '프로필 수정 실패');
    } catch (err) {
      throw new Error('프로필 수정에 실패했습니다: ' + pickErrorMessage(err));
    }
  },

  async changePassword(passwordData) {
    try {
      const res = await api.post('/api/user/password-change/', {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
        confirm_password: passwordData.confirmPassword,
      });
      if (res.data?.success) return res.data.message;
      throw new Error(res.data?.message || '비밀번호 변경 실패');
    } catch (err) {
      throw new Error('비밀번호 변경에 실패했습니다: ' + pickErrorMessage(err));
    }
  },

  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (err) {
      console.error('사용자 정보 파싱 오류:', err);
      return null;
    }
  },

  isAdmin() {
    try {
      const user = this.getCurrentUser();
      return user && user.auth === 'Y';
    } catch (err) {
      console.error('관리자 여부 확인 오류:', err);
      return false;
    }
  },

  getToken() {
    return localStorage.getItem('access_token');
  },

  updateCurrentUser(userData) {
    try {
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (err) {
      console.error('사용자 정보 저장 오류:', err);
    }
  },
};
