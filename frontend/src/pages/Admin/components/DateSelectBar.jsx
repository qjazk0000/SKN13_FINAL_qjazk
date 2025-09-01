import React, { useState, useEffect } from "react";

export default function DateSelectBar({ onDateChange, startDate, endDate, onClearDateFilter }) {
  const [start_date, setStartDate] = useState(startDate || "");
  const [end_date, setEndDate] = useState(endDate || "");


  const today = new Date().toISOString().split("T")[0];

  const startMax = end_date
    ? (end_date < today ? end_date : today)
    : today;


  // props가 변경될 때 내부 상태 업데이트
  useEffect(() => {
    setStartDate(startDate || "");
    setEndDate(endDate || "");
  }, [startDate, endDate]);

  // 날짜 변경 시 부모 컴포넌트에 알림
  const handleStartDateChange = (e) => {
    const newStartDate = e.target.value;
    setStartDate(newStartDate);
    if (onDateChange) {
      onDateChange(newStartDate, end_date);
    }
  };

  const handleEndDateChange = (e) => {
    const newEndDate = e.target.value;
    setEndDate(newEndDate);
    if (onDateChange) {
      onDateChange(start_date, newEndDate);
    }
  };

  return (
    <div className="flex space-x-2 items-center">
      <label className="font-medium text-gray-700">기간 선택:</label>
      <input
        type="date"
        value={start_date}
        onChange={handleStartDateChange}
        className="border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        max={startMax}
      />
      <span className="text-gray-500">~</span>
      <input
        type="date"
        value={end_date}
        onChange={handleEndDateChange}
        className="border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        min={start_date} 
        max={today}
      />
      {(start_date || end_date) && onClearDateFilter && (
        <button
          onClick={onClearDateFilter}
          className="ml-2 px-2 py-1 text-xs text-red-600 hover:text-red-800 border border-red-300 rounded hover:bg-red-50"
        >
          초기화
        </button>
      )}
    </div>
  );
}
