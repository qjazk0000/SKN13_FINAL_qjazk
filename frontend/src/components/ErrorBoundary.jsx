import React from "react";

export default class ErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError() { 
    return { hasError: true }; 
  }
  
  componentDidCatch(err, info) { 
    console.error("[ErrorBoundary]", err, info); 
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 text-center">
          <h2 className="text-xl font-bold text-red-600 mb-2">문제가 발생했습니다</h2>
          <p className="text-gray-600 mb-4">페이지를 새로고침하거나 다시 시도해주세요.</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            새로고침
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
} 