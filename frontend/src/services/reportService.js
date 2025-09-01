import api from "../services/api";

export const reportChat = async (chatId, errorType, reason) => {
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
    return response.data;
  } catch (error) {
    if (error.response) {
    throw new Error(JSON.stringify(error.response.data));
  } else {
    alert("신고 처리 중 알 수 없는 오류: " + error.message);
  }
  }
};