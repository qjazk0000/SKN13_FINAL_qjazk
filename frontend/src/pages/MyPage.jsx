import React from 'react';
import './MyPage.css';

function MyPage() {
  return (
    <div className="mypage-container">
      <div className="mypage-content">
        <h2>마이페이지</h2>
        
        <div className="profile-section">
          <div className="profile-info">
            <h3>사용자 정보</h3>
            <p><strong>이름:</strong> 홍길동</p>
            <p><strong>이메일:</strong> hong@example.com</p>
            <p><strong>부서:</strong> 개발팀</p>
          </div>
        </div>
        
        <div className="usage-section">
          <h3>사용 통계</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-number">42</span>
              <span className="stat-label">총 대화 수</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">15</span>
              <span className="stat-label">이번 주 대화</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">3</span>
              <span className="stat-label">업로드 파일</span>
            </div>
          </div>
        </div>
        
        <div className="actions-section">
          <h3>계정 관리</h3>
          <button className="action-button">비밀번호 변경</button>
          <button className="action-button">프로필 수정</button>
          <button className="action-button logout">로그아웃</button>
        </div>
      </div>
    </div>
  );
}

export default MyPage;
