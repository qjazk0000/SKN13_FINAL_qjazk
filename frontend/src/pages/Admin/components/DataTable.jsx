import React from "react";

function DataTable({ columns, data }) {
  return (
    <table className="w-full border border-gray-300">
      <thead>
        <tr className="bg-gray-100">
          {columns.map((col, index) => (
            <th key={index} className="border p-2 text-center">
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.length > 0 ? (
          data.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-gray-50">
              {columns.map((col, colIndex) => {
                // 영수증 보기 셀인지 확인
                const isReceiptCell = col.accessor === 'file_path';
                const hasPreview = isReceiptCell && row.previewOpen;
                
                return (
                  <td 
                    key={colIndex} 
                    className={`border p-2 text-center ${isReceiptCell ? 'receipt-preview-cell' : ''} ${hasPreview ? 'expanded' : ''}`}
                  >
                    {col.cell ? col.cell(row[col.accessor], row) : row[col.accessor]}
                  </td>
                );
              })}
            </tr>
          ))
        ) : (
          <tr>
            <td colSpan={columns.length} className="text-center p-4">
              데이터가 없습니다.
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}

export default DataTable;
