import React, { useState } from "react";

export default function DateSelectBar() {
  const [start_date, setStartDate] = useState("");
  const [end_date, setEndDate] = useState("");

  return (
    <div className="flex space-x-2 items-center">
      <label>기간 선택:</label>

      <input
        type="date"
        value={start_date}
        onChange={(e) => setStartDate(e.target.value)}
        className="border border-gray-300 rounded p-2"
      />

      <span>~</span>

      <input
        type="date"
        value={end_date}
        onChange={(e) => setEndDate(e.target.value)}
        className="border border-gray-300 rounded p-2"
        min={start_date} // 시작 날짜보다 이전 날짜 선택 방지
      />
    </div>
  );
}
