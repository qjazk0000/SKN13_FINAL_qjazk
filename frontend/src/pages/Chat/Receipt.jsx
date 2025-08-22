import React, { useState } from "react";
import { CloudArrowUpIcon, ArrowDownTrayIcon } from "@heroicons/react/24/solid";
import api from "../../services/api";

function Receipt({ selectedReceipt, selectedCategory }) {
  const [uploadFile, setUploadFile] = useState(null);
  // const [uploadFiles, setUploadFiles] = useState([]);
  const [reportDateRange, setReportDateRange] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploadFile(e.target.files[0]); // 첫 번째 파일만 저장
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) {
      alert("업로드할 파일을 선택해주세요.");
      return;
    }

    try {
      setIsLoading(true);

      const formData = new FormData();
      formData.append("files", uploadFile); // 서버에서 'files' 키로 받음

      const res = await api.post("/receipt/upload/", formData);
      alert("업로드 완료!");
      console.log("업로드 결과:", res.data);

      setUploadFile(null);
    } catch (error) {
      console.error("업로드 에러:", {
        status: error.response?.status,
        data: error.response?.data,
      });
      alert(
        error.response?.data?.detail ||
          error.response?.data?.message ||
          "업로드 실패"
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    // TODO: 영수증 보고서 다운로드 API 연동
    if (reportDateRange) {
      alert(`${reportDateRange} 기간 보고서 다운로드 요청`);
      console.log("영수증 보고서 다운로드:", reportDateRange);
    } else {
      alert("보고서 기간을 선택해주세요.");
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
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        <img
          src="/images/NAVI.png"
          alt="NAVI Logo"
          className="w-24 h-auto mb-4"
        />
        <div className="text-xl font-bold text-gray-700">
          "영수증 처리 도우미"
        </div>
        <p className="mt-4 text-gray-500">
          영수증 업로드와 보고서 추출 기능을 이용해보세요.
        </p>
      </div>

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
            <h3 className="text-lg font-semibold text-gray-800">보고서 추출</h3>
            <input
              type="month"
              value={reportDateRange}
              onChange={(e) => setReportDateRange(e.target.value)}
              className="w-full h-8 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
            <input
              type="month"
              value={reportDateRange}
              onChange={(e) => setReportDateRange(e.target.value)}
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
