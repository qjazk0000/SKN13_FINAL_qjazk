import React, { useState, useEffect } from 'react';
import { authService } from '../../services/authService';
import './MyPage.css';

function MyPage() {
  const [userInfo, setUserInfo] = useState({
    username: '',
    email: '',
    dept: '',
    rank: '',
    user_id: '',
    created_dt: '',
    auth: ''
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [isProfileLoading, setIsProfileLoading] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 페이지 로드 시 사용자 프로필 조회
  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        setIsProfileLoading(true);
        setError('');
        const profileData = await authService.getUserProfile();
        setUserInfo(profileData);
      } catch (error) {
        setError('프로필 조회에 실패했습니다: ' + error.message);
      } finally {
        setIsProfileLoading(false);
      }
    };
    
    fetchUserProfile();
  }, []);

  const handleUserInfoChange = (field, value) => {
    setUserInfo(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePasswordChange = (field, value) => {
    setPasswordData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // 프로필 정보 수정
  const handleUserInfoUpdate = async () => {
    try {
      setIsLoading(true);
      setError('');
      setSuccess('');
      
      const updatedProfile = await authService.updateUserProfile(userInfo);
      setUserInfo(updatedProfile);
      setSuccess('프로필이 성공적으로 업데이트되었습니다.');
    } catch (error) {
      setError('프로필 업데이트에 실패했습니다: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // 비밀번호 변경
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // 클라이언트 측 검증
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('새 비밀번호가 일치하지 않습니다.');
      return;
    }

    if (passwordData.newPassword.length < 8) {
      setError('새 비밀번호는 최소 8자 이상이어야 합니다.');
      return;
    }

    try {
      setIsLoading(true);
      
      await authService.changePassword({
        currentPassword: passwordData.currentPassword,
        newPassword: passwordData.newPassword,
        confirmPassword: passwordData.confirmPassword
      });
      
      setSuccess('비밀번호가 성공적으로 변경되었습니다.');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      setError('비밀번호 변경에 실패했습니다: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mypage-container">
      <div className="mypage-content">
        <h2>마이페이지</h2>
        
        <div className="mypage-sections">
          {/* 사용자 정보 섹션 */}
          <div className="user-info-section">
            <div className="profile-header">
              <div className="profile-avatar">
                <div className="avatar-icon">👤</div>
              </div>
              <div className="profile-details">
                {isProfileLoading ? (
                  <div>프로필 정보를 불러오는 중...</div>
                ) : (
                  <>
                    <h3 className="user-name">{userInfo.username || '사용자명 없음'}</h3>
                    <p className="user-email">{userInfo.email || '이메일 없음'}</p>
                  </>
                )}
              </div>
            </div>
            
            <div className="user-fields">
              <div className="field-group">
                <label>아이디 (ID)</label>
                <input
                  type="text"
                  value={userInfo.username || ''}
                  onChange={(e) => handleUserInfoChange('username', e.target.value)}
                  className="info-input"
                  disabled={isProfileLoading}
                />
              </div>
              
              <div className="field-group">
                <label>부서 (Department)</label>
                <input
                  type="text"
                  value={userInfo.dept || ''}
                  onChange={(e) => handleUserInfoChange('dept', e.target.value)}
                  className="info-input"
                  disabled={isProfileLoading}
                />
              </div>
              
              <div className="field-group">
                <label>직급 (Position)</label>
                <input
                  type="text"
                  value={userInfo.rank || ''}
                  onChange={(e) => handleUserInfoChange('rank', e.target.value)}
                  className="info-input"
                  disabled={isProfileLoading}
                />
              </div>
              
              <div className="field-group">
                <label>사용자 ID (User ID)</label>
                <input
                  type="text"
                  value={userInfo.user_id || ''}
                  className="info-input"
                  disabled={true}
                  readOnly
                />
              </div>
              
              <div className="field-group">
                <label>가입일시 (Created Date)</label>
                <input
                  type="text"
                  value={userInfo.created_dt ? new Date(userInfo.created_dt).toLocaleString('ko-KR') : ''}
                  className="info-input"
                  disabled={true}
                  readOnly
                />
              </div>
              
              <div className="field-group">
                <label>인증상태 (Auth Status)</label>
                <input
                  type="text"
                  value={userInfo.auth === 'Y' ? '인증됨' : '미인증'}
                  className="info-input"
                  disabled={true}
                  readOnly
                />
              </div>
            </div>

            {/* 프로필 수정 버튼 */}
            <button 
              onClick={handleUserInfoUpdate}
              className="update-profile-button"
              disabled={isLoading || isProfileLoading}
            >
              {isLoading ? '저장 중...' : '프로필 수정'}
            </button>
          </div>

          {/* 비밀번호 관리 섹션 */}
          <div className="password-section">
            <h3>비밀번호 관리</h3>
            
            <form onSubmit={handlePasswordSubmit}>
              <div className="field-group">
                <label>현재 비밀번호 (Current Password)</label>
                <input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
                  className="password-input"
                  placeholder="********"
                  required
                  disabled={isLoading}
                />
              </div>
              
              <div className="field-group">
                <label>새 비밀번호 (New Password)</label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
                  className="password-input"
                  placeholder="새 비밀번호를 입력하세요 (8자 이상)"
                  required
                  disabled={isLoading}
                />
              </div>
              
              <div className="field-group">
                <label>비밀번호 확인 (Confirm Password)</label>
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
                  className="password-input"
                  placeholder="새 비밀번호를 다시 입력하세요"
                  required
                  disabled={isLoading}
                />
              </div>

              {error && <p className="error-message">{error}</p>}
              {success && <p className="success-message">{success}</p>}
              
              <button type="submit" className="submit-button" disabled={isLoading}>
                {isLoading ? '저장 중...' : '비밀번호 변경'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MyPage;
