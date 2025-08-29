import React from "react";

function CustomModal({
  open,
  title = "알림",
  message = "",
  confirmText = "확인",
  cancelText = "취소",
  onConfirm,
  onCancel,
  children,
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
      <div className="bg-white rounded-lg shadow-lg p-6 min-w-[300px] max-w-[90vw]">
        {title && (
          <div className="text-lg font-bold mb-2 text-gray-800">{title}</div>
        )}
        {message && <div className="mb-4 text-gray-700">{message}</div>}
        {children}
        <div className="flex justify-end gap-2 mt-6">
          {cancelText && (
            <button
              className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition"
              onClick={onCancel}
            >
              {cancelText}
            </button>
          )}
          {confirmText && (
            <button
              className="px-4 py-2 bg-orange-400 text-white rounded hover:bg-orange-500 transition"
              onClick={onConfirm}
            >
              {confirmText}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default CustomModal;
