import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { authService } from '../../services/authService';

function AdminProtectedRoute({ children }) {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    const checkAdminAuth = async () => {
      try {
        // 현재 사용자 정보 확인
        const currentUser = authService.getCurrentUser();
        
        if (!currentUser) {
          // 로그인되지 않은 경우
          setIsAuthorized(false);
          setIsLoading(false);
          return;
        }

        // 관리자 권한 확인 (authService의 isAdmin 함수 사용)
        if (authService.isAdmin()) {
          setIsAuthorized(true);
        } else {
          setIsAuthorized(false);
        }
      } catch (error) {
        console.error('관리자 권한 확인 실패:', error);
        setIsAuthorized(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAdminAuth();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthorized) {
    // 관리자가 아닌 경우 채팅 페이지로 리다이렉트
    return <Navigate to="/chat" replace />;
  }

  // 관리자인 경우 자식 컴포넌트 렌더링
  return children;
}

export default AdminProtectedRoute;
