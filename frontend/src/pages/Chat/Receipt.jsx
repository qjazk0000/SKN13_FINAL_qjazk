import React, { useEffect, useState } from "react";
import { CloudArrowUpIcon, ArrowDownTrayIcon } from "@heroicons/react/24/solid";
import api from "../../services/api";
import CustomModal from "./CustomModal";
import LoadingMask from "../../components/LoadingMask";

function Receipt({ selectedReceipt, receiptDetails, onSaveSuccess }) {
  const [uploadFile, setUploadFile] = useState(null);
  const [receiptInfo, setReceiptInfo] = useState(null);
  const [editInfo, setEditInfo] = useState(null);

  const [reportStart, setReportStart] = useState("");
  const [reportEnd, setReportEnd] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [saveModalOpen, setSaveModalOpen] = useState(false);
  const today = new Date().toISOString().slice(0, 7);
  const [currentIndex, setCurrentIndex] = useState(0);

  // 여러 장 지원: receiptInfo가 배열이면 현재 인덱스의 결과만 사용
  const isMulti = Array.isArray(receiptInfo) && receiptInfo.length > 0;
  // const currentReceiptInfo = isMulti ? receiptInfo[currentIndex] : receiptInfo;
  const currentEditInfo = isMulti && editInfo && Array.isArray(editInfo)
    ? editInfo[currentIndex]
    : editInfo;

  useEffect(() => {
    if (receiptDetails) {
      // setReceiptInfo(null);

      // extracted_text 문자열 파싱
      let extracted = {};
      if (typeof receiptDetails.extracted_text === "string") {
        try {
          const jsonStr = receiptDetails.extracted_text.replace(/'/g, '"');
          extracted = JSON.parse(jsonStr);
        } catch (e) {
          extracted = {};
        }
      } else if (typeof receiptDetails.extracted_text === "object") {
        extracted = receiptDetails.extracted_text;
      }

      setReceiptInfo({
        ...receiptDetails,
        extracted,
      });

      setEditInfo({
        결제처: receiptDetails.store_name || extracted.결제처 || "",
        결제일시: receiptDetails.payment_date || extracted.결제일시 || "",
        총합계: receiptDetails.amount || extracted.총합계 || 0,
        카드정보: extracted.카드정보 || "",
        품목: Array.isArray(extracted.품목)
          ? extracted.품목.map((item) => ({ ...item }))
          : [],
      });
    }
  }, [receiptDetails]);

  // 여러 장 지원: receiptInfo가 배열이면 현재 인덱스의 결과만 사용
  useEffect(() => {
    if (Array.isArray(receiptInfo)) {
      setEditInfo(receiptInfo.map(info => ({
        결제처: info.extracted?.결제처 || "",
        결제일시: info.extracted?.결제일시 || "",
        총합계: info.extracted?.총합계 || 0,
        카드정보: info.extracted?.카드정보 || "",
        품목: Array.isArray(info.extracted?.품목)
          ? info.extracted.품목.map(item => ({ ...item }))
          : [],
      })));
    } else if (receiptDetails) {
      setReceiptInfo(null);

      // extracted_text 문자열 파싱
      let extracted = {};
      if (typeof receiptDetails.extracted_text === "string") {
        try {
          const jsonStr = receiptDetails.extracted_text.replace(/'/g, '"');
          extracted = JSON.parse(jsonStr);
        } catch (e) {
          extracted = {};
        }
      } else if (typeof receiptDetails.extracted_text === "object") {
        extracted = receiptDetails.extracted_text;
      }

      setEditInfo({
        결제처: receiptDetails.store_name || extracted.결제처 || "",
        결제일시: receiptDetails.payment_date || extracted.결제일시 || "",
        총합계: receiptDetails.amount || extracted.총합계 || 0,
        카드정보: extracted.카드정보 || "",
        품목: Array.isArray(extracted.품목)
          ? extracted.품목.map((item) => ({ ...item }))
          : [],
      });
    } else if (receiptInfo) {
      setEditInfo({
        결제처: receiptInfo.extracted?.결제처 || "",
        결제일시: receiptInfo.extracted?.결제일시 || "",
        총합계: receiptInfo.extracted?.총합계 || 0,
        카드정보: receiptInfo.extracted?.카드정보 || "",
        품목: receiptInfo.extracted?.품목
          ? receiptInfo.extracted.품목.map((item) => ({ ...item }))
          : [],
      });
    } else {
      setEditInfo(null);
    }
  }, [receiptDetails, receiptInfo]);

  // 품목/필드 변경 핸들러도 배열 지원
  const handleEditChange = (field, value) => {
    if (isMulti) {
      setEditInfo((prev) =>
        prev.map((info, idx) =>
          idx === currentIndex ? { ...info, [field]: value } : info
        )
      );
    } else {
      setEditInfo((prev) => ({ ...prev, [field]: value }));
    }
  };

  const handleItemChange = (idx, field, value) => {
    if (isMulti) {
      setEditInfo((prev) =>
        prev.map((info, i) =>
          i === currentIndex
            ? {
                ...info,
                품목: info.품목.map((item, j) =>
                  j === idx ? { ...item, [field]: value } : item
                ),
              }
            : info
        )
      );
    } else {
      setEditInfo((prev) => ({
        ...prev,
        품목: prev.품목.map((item, i) =>
          i === idx ? { ...item, [field]: value } : item
        ),
      }));
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploadFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) {
      alert("업로드할 파일을 선택해주세요.");
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append("files", uploadFile);

      const response = await api.post("/receipt/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
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
    } finally {
      setIsLoading(false);
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
        responseType: "blob",
      });

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

  // 저장 시 현재 인덱스의 영수증만 저장
  const handleSave = async () => {
    // 여러 장 처리
    const isMulti = Array.isArray(receiptInfo) && receiptInfo.length > 0;
    const currentEdit = isMulti ? editInfo[currentIndex] : editInfo;
    const currentReceipt = isMulti ? receiptInfo[currentIndex] : receiptInfo;

    if (!currentReceipt || !currentEdit) {
      alert("저장할 영수증 정보가 없습니다.");
      return;
    }
    setIsLoading(true);
    try {
      const payload = {
        receipts: editInfo.map((info, idx) => ({
          file_id: receiptInfo[idx].file_id,
          store_name: info.결제처,
          payment_date: info.결제일시,
          amount: Number(info.총합계),
          card_info: info.카드정보,
          items: Array.isArray(info.품목)
            ? info.품목.map(item => ({
                품명: item.품명,
                단가: Number(item.단가),
                수량: Number(item.수량),
                금액: Number(item.금액),
              }))
            : [],
        }))
      };
      console.log(payload);
      const response = await api.post("/receipt/save/", payload);
      if (response.data.success) {
        alert("영수증이 성공적으로 저장되었습니다.");
        if (onSaveSuccess) onSaveSuccess();
        // 저장 후 다음 영수증으로 이동
        setReceiptInfo(null);
        setEditInfo(null);
        setUploadFile(null);
      } else {
        alert(response.data.message || "저장에 실패했습니다.");
      }
    } catch (error) {
      console.error("영수증 저장 오류:", error);
      alert(error.response?.data?.message || "저장 중 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
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

  const isViewingExisting = !!receiptDetails;
  const isEditing = !!editInfo;

  return (
    <div className="flex flex-col w-full h-screen bg-gray-100 sm:px-8 md:px-16 lg:px-32 xl:px-60">
      {isLoading && (
        <LoadingMask isVisible={isLoading} message="영수증 처리 중..." />
      )}

      {isEditing ? (
        <div className="flex-1 overflow-y-auto py-4">
          <div className="bg-white rounded-lg shadow-md p-6 max-w-xl mx-auto">
            {isMulti && (
              <div className="flex justify-between items-center mb-4">
                <button
                  onClick={() => setCurrentIndex((i) => Math.max(i - 1, 0))}
                  disabled={currentIndex === 0}
                  className="px-3 py-1 bg-gray-200 rounded"
                >
                  ◀
                </button>
                <span className="font-bold">
                  {currentIndex + 1} / {receiptInfo.length}
                </span>
                <button
                  onClick={() =>
                    setCurrentIndex((i) =>
                      Math.min(i + 1, receiptInfo.length - 1)
                    )
                  }
                  disabled={currentIndex === receiptInfo.length - 1}
                  className="px-3 py-1 bg-gray-200 rounded"
                >
                  ▶
                </button>
              </div>
            )}
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              {isViewingExisting ? "영수증 상세 정보" : "영수증 정보 편집"}
            </h2>
            <div className="space-y-3">
              {receiptInfo?.file_name && (
                <div className="flex items-center">
                  <span className="w-32 text-gray-500 font-semibold">
                    파일명
                  </span>
                  <span className="text-gray-700">{receiptInfo.file_name}</span>
                </div>
              )}
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">결제처</span>
                <input
                  type="text"
                  className="border rounded px-2 py-1 flex-1"
                  value={currentEditInfo.결제처}
                  onChange={(e) => handleEditChange("결제처", e.target.value)}
                  readOnly={isViewingExisting && receiptDetails?.status !== "pending"}
                />
              </div>
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">
                  결제일시
                </span>
                <input
                  type="text"
                  className="border rounded px-2 py-1 flex-1"
                  value={currentEditInfo.결제일시}
                  onChange={(e) => handleEditChange("결제일시", e.target.value)}
                  readOnly={isViewingExisting && receiptDetails?.status !== "pending"}
                />
              </div>
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">
                  카드정보
                </span>
                <input
                  type="text"
                  className="border rounded px-2 py-1 flex-1"
                  value={currentEditInfo.카드정보}
                  onChange={(e) => handleEditChange("카드정보", e.target.value)}
                  readOnly={isViewingExisting && receiptDetails?.status !== "pending"}
                />
              </div>
              <div className="flex items-center">
                <span className="w-32 text-gray-500 font-semibold">총합계</span>
                <input
                  type="number"
                  className="border rounded px-2 py-1 flex-1"
                  value={currentEditInfo.총합계}
                  onChange={(e) => handleEditChange("총합계", e.target.value)}
                  readOnly={isViewingExisting && receiptDetails?.status !== "pending"}
                />
              </div>
              {currentEditInfo.품목?.length > 0 && (
                <div>
                  <span className="w-32 text-gray-500 font-semibold">품목</span>
                  <div className="overflow-x-auto">
                    <table className="min-w-full mt-2 text-sm border">
                      <thead className="bg-gray-100">
                        <tr>
                          <th className="px-2 py-1 border">품명</th>
                          <th className="px-2 py-1 border">단가</th>
                          <th className="px-2 py-1 border">수량</th>
                          <th className="px-2 py-1 border">금액</th>
                        </tr>
                      </thead>
                      <tbody>
                        {currentEditInfo.품목.map((item, idx) => (
                          <tr key={idx}>
                            <td className="px-2 py-1 border">
                              <input
                                type="text"
                                className="border rounded px-1 py-0.5 w-full"
                                value={item.품명}
                                onChange={(e) =>
                                  handleItemChange(idx, "품명", e.target.value)
                                }
                                readOnly={isViewingExisting && receiptDetails?.status !== "pending"}
                              />
                            </td>
                            <td className="px-2 py-1 border">
                              <input
                                type="number"
                                className="border rounded px-1 py-0.5 w-full"
                                value={item.단가}
                                onChange={(e) =>
                                  handleItemChange(idx, "단가", e.target.value)
                                }
                                readOnly={isViewingExisting && receiptDetails?.status !== "pending"}
                              />
                            </td>
                            <td className="px-2 py-1 border">
                              <input
                                type="number"
                                className="border rounded px-1 py-0.5 w-full"
                                value={item.수량}
                                onChange={(e) =>
                                  handleItemChange(idx, "수량", e.target.value)
                                }
                                readOnly={isViewingExisting && receiptDetails?.status !== "pending"}
                              />
                            </td>
                            <td className="px-2 py-1 border">
                              <input
                                type="number"
                                className="border rounded px-1 py-0.5 w-full"
                                value={item.금액}
                                onChange={(e) =>
                                  handleItemChange(idx, "금액", e.target.value)
                                }
                                readOnly={isViewingExisting && receiptDetails?.status !== "pending"}
                              />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
            {/* status가 pending인 경우에만 최종 저장 버튼 노출 */}
            {isEditing && (receiptDetails && receiptDetails.status === "pending") && (
              <div className="mt-6 flex justify-center">
                <button
                  className="px-4 py-2 bg-orange-300 text-white rounded-lg shadow hover:bg-orange-400"
                  onClick={() => setSaveModalOpen(true)}
                >
                  최종 저장
                </button>
              </div>
            )}
          </div>
        </div>
      ) : (
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
            영수증 업로드와 다운로드 기능을 이용해보세요.
          </p>
        </div>
      )}

      {saveModalOpen && (
        <CustomModal
          open={saveModalOpen}
          title="영수증 저장"
          message="영수증 정보를 최종 저장하시겠습니까?"
          confirmText="저장하기"
          cancelText="취소하기"
          onConfirm={() => {
            handleSave();
            setSaveModalOpen(false);
          }}
          onCancel={() => setSaveModalOpen(false)}
        />
      )}

      {selectedReceipt?.isNew && !isEditing && (
        <div className="flex justify-center flex-shrink-0 p-4">
          <div className="flex flex-col md:flex-row bg-white shadow-md rounded-lg w-full max-w-4xl p-4 gap-4">
            <div className="flex-1 flex flex-col justify-between items-center p-4 rounded-md gap-2">
              <h3 className="text-lg font-semibold">영수증 업로드</h3>
              <label
                htmlFor="file-upload"
                className="flex items-center justify-center p-2 border-2 border-dashed border-gray-300 cursor-pointer hover:bg-gray-50 w-full h-16"
              >
                <input
                  id="file-upload"
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                />
                {uploadFile ? (
                  <span className="font-semibold">{uploadFile.name}</span>
                ) : (
                  <>
                    <CloudArrowUpIcon className="h-8 w-8 text-gray-400 m-2" />
                    <span className="font-semibold">파일을 선택하세요</span>
                  </>
                )}
              </label>
              <button
                onClick={handleUpload}
                className="px-4 py-2 bg-gray-200 rounded-lg shadow-md hover:bg-gray-300 w-full cursor-pointer"
                disabled={isLoading || !uploadFile}
              >
                {isLoading ? "처리 중..." : "업로드"}
              </button>
            </div>
            <div className="flex-1 flex flex-col gap-2 justify-between items-center p-4 rounded-md">
              <h3 className="text-lg font-semibold">영수증 다운로드</h3>
              <input
                type="month"
                value={reportStart}
                onChange={(e) => setReportStart(e.target.value)}
                className="w-full h-8 p-2 border rounded-md"
                max={reportEnd || today}
              />
              <input
                type="month"
                value={reportEnd}
                onChange={(e) => setReportEnd(e.target.value)}
                className="w-full p-2 h-8 border rounded-md"
                min={reportStart || undefined}
              />
              <button
                onClick={handleDownload}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-200 rounded-lg shadow-lg hover:bg-gray-300 w-full justify-center"
              >
                <ArrowDownTrayIcon className="h-5 w-5" />
                <span>다운로드</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ReceiptPreviewMulti({ results }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!results || results.length === 0) return null;

  const current = results[currentIndex];

  return (
    <div className="w-full flex flex-col items-center">
      <div className="flex items-center mb-4">
        <button
          disabled={currentIndex === 0}
          onClick={() => setCurrentIndex(i => i - 1)}
          className="px-3 py-1 bg-gray-200 rounded mr-2"
        >
          ◀
        </button>
        <span className="font-bold">
          {currentIndex + 1} / {results.length}
        </span>
        <button
          disabled={currentIndex === results.length - 1}
          onClick={() => setCurrentIndex(i => i + 1)}
          className="px-3 py-1 bg-gray-200 rounded ml-2"
        >
          ▶
        </button>
      </div>
      <div className="w-full bg-gray-50 rounded-lg p-4 border">
        <div className="mb-2 text-base text-gray-800">
          <span className="font-semibold">파일명: </span>
          {current.file_name}
        </div>
        <div className="mb-2 text-base text-gray-800">
          <span className="font-semibold">결제처: </span>
          {current.extracted?.결제처 || "정보 없음"}
        </div>
        <div className="mb-2 text-base text-gray-800">
          <span className="font-semibold">결제일시: </span>
          {current.extracted?.결제일시 || "정보 없음"}
        </div>
        <div className="mb-2 text-base text-gray-800">
          <span className="font-semibold">총합계: </span>
          {current.extracted?.총합계 || "정보 없음"}
        </div>
        <div className="mb-2 text-base text-gray-800">
          <span className="font-semibold">카드정보: </span>
          {current.extracted?.카드정보 || "정보 없음"}
        </div>
        {current.extracted?.품목 && current.extracted.품목.length > 0 && (
          <div className="mt-2">
            <span className="font-semibold">품목:</span>
            <div className="mt-1">
              {current.extracted.품목.map((item, idx) => (
                <div
                  key={idx}
                  className="flex justify-between text-gray-700 text-sm py-1"
                >
                  <span>{item.품명}</span>
                  <span>
                    {item.수량} x {item.단가} = {item.금액}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Receipt;
export { ReceiptPreviewMulti };
