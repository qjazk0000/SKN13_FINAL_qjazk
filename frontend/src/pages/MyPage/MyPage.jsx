import React, { useState } from 'react';
import './MyPage.css';

function MyPage() {
  const [userInfo, setUserInfo] = useState({
    id: '개발-001',
    department: '개발2팀',
    position: '사원'
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // 비밀번호 확인 검증
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('새 비밀번호가 일치하지 않습니다.');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      setError('새 비밀번호는 최소 6자 이상이어야 합니다.');
      return;
    }

    try {
      // API 호출 로직 구현
      const response = await fetch('/api/accounts/update-password', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword
        }),
      });

      if (!response.ok) {
        throw new Error('비밀번호 변경 실패');
      }

      setSuccess('비밀번호가 성공적으로 변경되었습니다.');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (err) {
      setError('비밀번호 변경 중 오류가 발생했습니다.');
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
                <h3 className="user-name">최성장</h3>
                <p className="user-email">growing@gmail.com</p>
              </div>
            </div>
            
            <div className="user-fields">
              <div className="field-group">
                <label>아이디 (ID)</label>
                <input
                  type="text"
                  value={userInfo.id}
                  onChange={(e) => handleUserInfoChange('id', e.target.value)}
                  className="info-input"
                />
              </div>
              
              <div className="field-group">
                <label>부서 (Department)</label>
                <input
                  type="text"
                  value={userInfo.department}
                  onChange={(e) => handleUserInfoChange('department', e.target.value)}
                  className="info-input"
                />
              </div>
              
              <div className="field-group">
                <label>직급 (Position)</label>
                <input
                  type="text"
                  value={userInfo.position}
                  onChange={(e) => handleUserInfoChange('position', e.target.value)}
                  className="info-input"
                />
              </div>
            </div>
          </div>

          {/* 비밀번호 관리 섹션 */}
          <div className="password-section">
            <h3>비밀번호 관리</h3>
            
            <form onSubmit={handleSubmit}>
              <div className="field-group">
                <label>현재 비밀번호 (Current Password)</label>
                <input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
                  className="password-input"
                  placeholder="********"
                  required
                />
              </div>
              
              <div className="field-group">
                <label>새 비밀번호 (New Password)</label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
                  className="password-input"
                  placeholder="새 비밀번호를 입력하세요"
                  required
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
                />
              </div>

              {error && <p className="error-message">{error}</p>}
              {success && <p className="success-message">{success}</p>}
              
              <button type="submit" className="submit-button">
                수정하기
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MyPage;
