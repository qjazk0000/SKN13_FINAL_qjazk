import React, { useState } from "react";
import { CloudArrowUpIcon, ArrowDownTrayIcon } from "@heroicons/react/24/solid";
import api from "../../services/api";

function Receipt({ selectedReceipt, selectedCategory }) {
  const [uploadFile, setUploadFile] = useState(null);
  // const [uploadFiles, setUploadFiles] = useState([]);
  const [receiptInfo, setReceiptInfo] = useState(null);
  const [reportStart, setReportStart] = useState("");
  const [reportEnd, setReportEnd] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploadFile(e.target.files[0]); // 첫 번째 파일만 저장
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) {
      alert("업로드할 파일을 선택해주세요.");
    } else {
      alert(`${uploadFile.name} 파일 업로드 요청`);
      console.log("영수증 업로드:", uploadFile.name);
    }

    try {
      const formData = new FormData();
      formData.append("files", uploadFile);

      const response = await api.post("/receipt/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data.success) {
        setReceiptInfo(response.data.data);
        console.log("영수증 처리 내역:", response.data.data);
      } else {
        alert(response.data.message || "텍스트 추출 실패");
      }
    } catch (error) {
      console.error("텍스트 추출 오류:", error);
      alert(
        error.response?.data?.message || "텍스트 추출 중 오류가 발생했습니다."
      );
    }
  };

  const handleDownload = async () => {
    if (!reportStart || !reportEnd) {
      alert("기간을 선택해주세요.");
      return;
    }

    try {
      const response = await api.get("/receipt/download/", {
        params: { start_date: reportStart, end_date: reportEnd },
        responseType: "blob", // 파일 다운로드 시 필수
      });

      // 파일 저장
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `receipt_data_${reportStart}_${reportEnd}.csv`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();

      alert("다운로드 성공!");
    } catch (error) {
      console.error("다운로드 오류:", error);
      alert(
        error.response?.data?.message || "다운로드 중 오류가 발생했습니다."
      );
    }
  };

  const handleSave = async () => {
    if (!receiptInfo) {
      alert("저장할 영수증 정보가 없습니다.");
      return;
    }
    try {
      const payload = {
        file_id: receiptInfo.file_id,
        store_name: receiptInfo.extracted?.storeName || "",
        payment_date: receiptInfo.extracted?.transactionDate || "",
        amount: receiptInfo.extracted?.transactionAmount || 0,
        card_info: receiptInfo.extracted?.cardNumber || "",
        items: receiptInfo.extracted?.items || [],
      };
      const response = await api.post("/receipt/save/", payload);
      if (response.data.success) {
        alert("영수증이 성공적으로 저장되었습니다.");
      } else {
        alert(response.data.message || "저장에 실패했습니다.");
      }
    } catch (error) {
      console.error("영수증 저장 오류:", error);
      alert(error.response?.data?.message || "저장 중 오류가 발생했습니다.");
    }
  };

  if (!selectedReceipt) {
    return (
      <div className="flex flex-col items-center justify-center h-[100dvh] text-gray-500">
        <img
          src="/images/NAVI.png"
          alt="NAVI Logo"
          className="w-24 h-auto mb-4"
        />
        <div className="text-xl font-bold text-gray-700">
          영수증 처리 도우미
        </div>
        <p className="mt-4">영수증을 선택하거나 새 영수증을 생성하세요.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col w-full h-[100dvh] bg-gray-100 sm:px-8 md:px-16 lg:px-32 xl:px-60">
      {receiptInfo === null && (
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          <img
            src="/images/NAVI.png"
            alt="NAVI Logo"
            className="w-24 h-auto mb-4"
          />
          <div className="text-xl font-bold text-gray-700">
            영수증 처리 도우미
          </div>
          <p className="mt-4 text-gray-500">
            영수증 업로드와 보고서 추출 기능을 이용해보세요.
          </p>
        </div>
      )}
      {receiptInfo && (
        <div className="flex-1 overflow-y-auto py-4">
          <div className="bg-white rounded-lg shadow-md p-6 max-w-xl mx-auto">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              영수증 정보 확인
            </h2>
            <div className="space-y-3">
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">파일명</span>
                <span className="text-gray-700">{receiptInfo.file_name}</span>
              </div>
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">결제처</span>
                <span className="text-gray-700">
                  {receiptInfo.extracted?.storeName || "-"}
                </span>
              </div>
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">
                  결제일시
                </span>
                <span className="text-gray-700">
                  {receiptInfo.extracted?.transactionDate || "-"}
                </span>
              </div>
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">카드사</span>
                <span className="text-gray-700">
                  {receiptInfo.extracted?.cardCompany || "-"}
                </span>
              </div>
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">
                  카드번호
                </span>
                <span className="text-gray-700">
                  {receiptInfo.extracted?.cardNumber || "-"}
                </span>
              </div>
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">총합계</span>
                <span className="text-gray-700">
                  {receiptInfo.extracted?.transactionAmount
                    ? `${receiptInfo.extracted.transactionAmount.toLocaleString()}원`
                    : "-"}
                </span>
              </div>
              {/* 품목 정보가 있을 경우 */}
              {receiptInfo.extracted?.items &&
                Array.isArray(receiptInfo.extracted.items) && (
                  <div>
                    <span className="w-32 text-gray-500 font-semibold">
                      품목
                    </span>
                    <div className="overflow-x-auto">
                      <table className="min-w-full mt-2 text-sm text-left border">
                        <thead>
                          <tr className="bg-gray-100">
                            <th className="px-2 py-1 border">상품명</th>
                            <th className="px-2 py-1 border">단가</th>
                            <th className="px-2 py-1 border">수량</th>
                            <th className="px-2 py-1 border">금액</th>
                          </tr>
                        </thead>
                        <tbody>
                          {receiptInfo.extracted.items.map((item, idx) => (
                            <tr key={idx}>
                              <td className="px-2 py-1 border">
                                {item.productName}
                              </td>
                              <td className="px-2 py-1 border">
                                {item.unitPrice.toLocaleString()}원
                              </td>
                              <td className="px-2 py-1 border">
                                {item.quantity}
                              </td>
                              <td className="px-2 py-1 border">
                                {item.totalPrice.toLocaleString()}원
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
            </div>
            <div className="mt-6 flex justify-center">
              <button
                className="px-4 py-2 bg-orange-300 text-white rounded-lg shadow hover:bg-orange-400 transition"
                onClick={handleSave}
              >
                최종 저장
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 메인 콘텐츠: 업로드 & 다운로드 박스 */}
      <div className="flex justify-center flex-shrink-0">
        <div className="flex bg-white rounded-lg w-full max-w-4xl p-4">
          {/* 영수증 업로드 영역 */}
          <div className="flex flex-1 flex-col justify-between items-center p-4 border-b md:border-b-0 md:border-r border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800">
              영수증 업로드
            </h3>
            {/* 파일 선택 UI */}
            <label
              htmlFor="file-upload"
              className="flex items-center justify-center p-2 border-2 border-dashed border-gray-300 cursor-pointer hover:bg-gray-50 transition-colors w-full h-16"
            >
              <input
                id="file-upload"
                type="file"
                className="hidden"
                onChange={handleFileChange}
              />
              {uploadFile ? (
                <span className="text-gray-700 font-semibold text-center">
                  {uploadFile.name}
                </span>
              ) : (
                <>
                  <CloudArrowUpIcon className="h-8 w-8 text-gray-400 m-2" />
                  <span className="text-gray-600 font-semibold text-center">
                    파일을 선택하세요
                  </span>
                </>
              )}
            </label>
            <button
              onClick={handleUpload}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg shadow-md hover:bg-gray-300 transition-colors w-full"
            >
              {isLoading ? "업로드 중..." : "업로드"}
            </button>
          </div>

          {/* 영수증 보고서 추출 영역 */}
          <div className="flex flex-1 flex-col gap-2 justify-between items-center p-4">
            <h3 className="text-lg font-semibold text-gray-800">
              영수증 데이터 추출
            </h3>
            <input
              type="month"
              value={reportStart}
              onChange={(e) => setReportStart(e.target.value)}
              className="w-full h-8 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
            <input
              type="month"
              value={reportEnd}
              onChange={(e) => setReportEnd(e.target.value)}
              className="w-full p-2 h-8 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
            <button
              onClick={handleDownload}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg shadow-lg hover:bg-gray-300 transition-colors w-full justify-center"
            >
              <ArrowDownTrayIcon className="h-5 w-5" />
              <span>다운로드</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Receipt;
