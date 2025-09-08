import api from "../services/api";

// 중복 요청 방지를 위한 Map (더 정확한 추적)
const pendingRequests = new Map();

export const reportChat = async (chatId, errorType, reason) => {
  const requestKey = `${chatId}-${errorType}-${reason}`;
  
  // 이미 진행 중인 동일한 요청이 있으면 기다림
  if (pendingRequests.has(requestKey)) {
    console.log(`🚫 중복 요청 방지: ${requestKey}`);
    return pendingRequests.get(requestKey);
  }
  
  const requestId = Date.now() + Math.random();
  console.log(`🚀 신고 요청 시작 [${requestId}] - chatId: ${chatId}, errorType: ${errorType}`);
  
  // Promise를 생성하여 진행 중인 요청으로 표시
  const requestPromise = (async () => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await api.post(`/chat/${chatId}/report/`, {
        error_type: errorType,
        reason: reason
      },{
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json"
          },
        });
      console.log(`✅ 신고 요청 성공 [${requestId}] - response:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`❌ 신고 요청 실패 [${requestId}]:`, error);
      if (error.response) {
      throw new Error(JSON.stringify(error.response.data));
    } else {
      alert("신고 처리 중 알 수 없는 오류: " + error.message);
    }
    } finally {
      // 요청 완료 후 Map에서 제거
      pendingRequests.delete(requestKey);
    }
  })();
  
  // 진행 중인 요청으로 표시
  pendingRequests.set(requestKey, requestPromise);
  
  return requestPromise;
};