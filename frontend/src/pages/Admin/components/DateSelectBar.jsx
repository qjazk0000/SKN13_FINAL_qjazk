import React, { useState, useEffect } from "react";

export default function DateSelectBar({ onDateChange, startDate, endDate, onClearDateFilter }) {
  const [start_date, setStartDate] = useState(startDate || "");
  const [end_date, setEndDate] = useState(endDate || "");


  const today = new Date().toISOString().split("T")[0];


  // props가 변경될 때 내부 상태 업데이트
  useEffect(() => {
    setStartDate(startDate || "");
    setEndDate(endDate || "");
  }, [startDate, endDate]);

  // 시작 날짜 변경 시
  const handleStartDateChange = (e) => {
    const newStartDate = e.target.value;
    setStartDate(newStartDate);

    // end_date가 선택되어 있는데 start > end 면 end 초기화
    if (end_date && newStartDate > end_date) {
      setEndDate("");
      onDateChange(newStartDate, "");
    } else {
      onDateChange(newStartDate, end_date);
    }
  };

  // 종료 날짜 변경 시
  const handleEndDateChange = (e) => {
    const newEndDate = e.target.value;
    setEndDate(newEndDate);

    // start_date가 선택되어 있는데 end < start 면 start 초기화
    if (start_date && newEndDate < start_date) {
      setStartDate("");
      onDateChange("", newEndDate);
    } else {
      onDateChange(start_date, newEndDate);
    }
  };

  return (
    <div className="flex space-x-2 items-center">
      <label className="font-medium text-gray-700">기간 선택:</label>
      <input
        type="date"
        value={start_date}
        max={end_date || today}   // 종료일보다 크지 않게 제한
        onChange={handleStartDateChange}
        className="border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <span className="text-gray-500">~</span>
      <input
        type="date"
        value={end_date}
        min={start_date || undefined}   // 시작일보다 작지 않게 제한
        max={today}
        onChange={handleEndDateChange}
        className="border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        onClick={onClearDateFilter}
        className="ml-2 px-2 py-1 text-xs text-red-600 hover:text-red-800 border border-red-300 rounded hover:bg-red-50"
      >
        초기화
      </button>
    </div>
  );
}