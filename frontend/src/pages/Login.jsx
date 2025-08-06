// ./fronted/src/pages/Login.jsx

import React, { useState } from 'react';
import './Login.css';

function Login() {
  const [userLoginId, setUserLoginId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    // 로그인 로직 구현
    setError('');

    try {
      const response = await fetch('/api/accounts/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_login_id: userLoginId,
          password: password,
        }),
      });

      if (!response.ok) {
        throw new Error('로그인 실패');
      }

      const data = await response.json();
      // 토큰 키 이름이 명세서에 없으니 백엔드 응답 구조 확인 필요
      if (data.token) {
        localStorage.setItem('token', data.token);
      }
      alert('로그인 성공!');
    } catch (err) {
      setError('아이디 또는 비밀번호가 올바르지 않습니다.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>로그인</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              placeholder="사용자명"
              value={userLoginID}
              onChange={(e) => setUserLoginId(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p style={{ color: 'red', textAlign: 'center'}}>{error}</p>}
          <button type="submit">로그인</button>
        </form>
      </div>
    </div>
  );
}

export default Login;
