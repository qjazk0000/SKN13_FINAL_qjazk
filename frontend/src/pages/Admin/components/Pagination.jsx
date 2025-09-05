import React from "react";

function Pagination({ currentPage, totalPages, onPageChange }) {
  // 한 번에 보여줄 페이지 버튼 개수
  const PAGE_GROUP_SIZE = 5;

  // 현재 그룹의 첫 페이지 번호 계산
  const groupStart = Math.floor((currentPage - 1) / PAGE_GROUP_SIZE) * PAGE_GROUP_SIZE + 1;
  // 현재 그룹의 마지막 페이지 번호 계산
  const groupEnd = Math.min(groupStart + PAGE_GROUP_SIZE - 1, totalPages);

  const pageNumbers = [];
  for (let i = groupStart; i <= groupEnd; i++) {
    pageNumbers.push(i);
  }

  return (
    <div className="flex justify-center items-center gap-2 mt-6">
      {/* 이전 그룹으로 이동 */}
      <button
        disabled={groupStart === 1}
        onClick={() => onPageChange(groupStart - 1)}
        className="px-2 py-1 rounded bg-gray-100 text-gray-700 hover:bg-gray-300"
      >
        &lt;
      </button>
      {/* 페이지 번호 버튼 */}
      {pageNumbers.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`px-3 py-1 rounded ${page === currentPage ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-300"}`}
        >
          {page}
        </button>
      ))}
      {/* 다음 그룹으로 이동 */}
      <button
        disabled={groupEnd === totalPages}
        onClick={() => onPageChange(groupEnd + 1)}
        className="px-2 py-1 rounded bg-gray-100 text-gray-700 hover:bg-gray-300"
      >
        &gt;
      </button>
    </div>
  );
}

export default Pagination;
