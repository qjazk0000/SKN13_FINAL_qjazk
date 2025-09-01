import React, { useState, useRef } from 'react';
import { authService } from '../services/authService';

const ReceiptUpload = ({ onUploadSuccess, onUploadError }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  // 파일 선택 처리
  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  // 파일 유효성 검사
  const validateAndSetFile = (file) => {
    // 파일 크기 제한 (10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      onUploadError('파일 크기는 10MB 이하여야 합니다.');
      return;
    }

    // 지원하는 파일 형식
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      onUploadError('지원하는 파일 형식: JPG, PNG, PDF');
      return;
    }

    setSelectedFile(file);
  };

  // 드래그 앤 드롭 처리
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  // 파일 업로드 처리
  const handleUpload = async () => {
    if (!selectedFile) {
      onUploadError('업로드할 파일을 선택해주세요.');
      return;
    }

    // 로그인 상태 확인
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      onUploadError('로그인이 필요합니다.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // FormData 생성
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('user_id', currentUser.user_id);

      // 업로드 진행률 시뮬레이션
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      // API 호출
      const response = await fetch('/api/receipt/upload/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`,
        },
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        onUploadSuccess(result.data);
        setSelectedFile(null);
        setUploadProgress(0);
      } else {
        throw new Error(result.message || '업로드에 실패했습니다.');
      }

    } catch (error) {
      console.error('Upload error:', error);
      onUploadError(error.message || '업로드 중 오류가 발생했습니다.');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  // 파일 제거
  const removeFile = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="receipt-upload">
      <div className="upload-container">
        {/* 드래그 앤 드롭 영역 */}
        <div
          className={`drag-drop-area ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          {!selectedFile ? (
            <div className="upload-prompt">
              <div className="upload-icon">📄</div>
              <p className="upload-text">
                영수증 이미지를 드래그하여 놓거나 클릭하여 선택하세요
              </p>
              <p className="upload-hint">
                지원 형식: JPG, PNG, PDF (최대 10MB)
              </p>
            </div>
          ) : (
            <div className="selected-file">
              <div className="file-info">
                <div className="file-icon">📄</div>
                <div className="file-details">
                  <p className="file-name">{selectedFile.name}</p>
                  <p className="file-size">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
              <button
                type="button"
                className="remove-file-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile();
                }}
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* 숨겨진 파일 입력 */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        {/* 업로드 버튼 */}
        {selectedFile && (
          <div className="upload-actions">
            <button
              type="button"
              className="upload-btn"
              onClick={handleUpload}
              disabled={isUploading}
            >
              {isUploading ? '업로드 중...' : '영수증 업로드'}
            </button>
            
            {isUploading && (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <span className="progress-text">{uploadProgress}%</span>
              </div>
            )}
          </div>
        )}
      </div>

      <style jsx>{`
        .receipt-upload {
          width: 100%;
          max-width: 600px;
          margin: 0 auto;
        }

        .upload-container {
          border: 2px dashed #e2e8f0;
          border-radius: 12px;
          padding: 2rem;
          text-align: center;
          transition: all 0.3s ease;
        }

        .drag-drop-area {
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .drag-drop-area:hover {
          border-color: #3b82f6;
          background-color: #f8fafc;
        }

        .drag-active {
          border-color: #3b82f6;
          background-color: #eff6ff;
        }

        .has-file {
          border-color: #10b981;
          background-color: #f0fdf4;
        }

        .upload-prompt {
          color: #64748b;
        }

        .upload-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .upload-text {
          font-size: 1.1rem;
          font-weight: 500;
          margin-bottom: 0.5rem;
        }

        .upload-hint {
          font-size: 0.9rem;
          color: #94a3b8;
        }

        .selected-file {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 1rem;
          background-color: #f8fafc;
          border-radius: 8px;
        }

        .file-info {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .file-icon {
          font-size: 2rem;
        }

        .file-name {
          font-weight: 500;
          margin: 0;
        }

        .file-size {
          color: #64748b;
          margin: 0;
          font-size: 0.9rem;
        }

        .remove-file-btn {
          background: none;
          border: none;
          color: #ef4444;
          font-size: 1.2rem;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 4px;
          transition: background-color 0.2s;
        }

        .remove-file-btn:hover {
          background-color: #fef2f2;
        }

        .upload-actions {
          margin-top: 1.5rem;
        }

        .upload-btn {
          background-color: #3b82f6;
          color: white;
          border: none;
          padding: 0.75rem 2rem;
          border-radius: 8px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .upload-btn:hover:not(:disabled) {
          background-color: #2563eb;
        }

        .upload-btn:disabled {
          background-color: #94a3b8;
          cursor: not-allowed;
        }

        .upload-progress {
          margin-top: 1rem;
        }

        .progress-bar {
          width: 100%;
          height: 8px;
          background-color: #e2e8f0;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 0.5rem;
        }

        .progress-fill {
          height: 100%;
          background-color: #10b981;
          transition: width 0.3s ease;
        }

        .progress-text {
          font-size: 0.9rem;
          color: #64748b;
        }
      `}</style>
    </div>
  );
};

export default ReceiptUpload;
