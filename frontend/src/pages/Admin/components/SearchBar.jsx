import React from "react";

function SearchBar({ 
    searchTerm, 
    setSearchTerm, 
    onSearch, 
    searchType, 
    setSearchType,
    searchOptions = [],
    onClearSearch,
    errorTypeOptions = []
}) {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="flex space-x-2 mb-4 p-2">
        {searchOptions.length > 0 && (
            <select 
                value={searchType} 
                onChange={(e) => setSearchType(e.target.value)}
                className="border border-gray-300 rounded p-2"
                >
                    {searchOptions.map(({value, label}) => (
                        <option key={value} value={value}>{label}</option>
                    ))}
                </select>
        )} 
      {searchType === 'error_type' ? (
        <select
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="border border-gray-300 rounded p-2 flex-1"
        >
          <option value="">신고 유형을 선택하세요</option>
          {errorTypeOptions.map(({value, label}) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      ) : (
        <input
          type="text"
          placeholder={
            searchOptions.find(opt => opt.value === searchType)?.label + " 입력" || "검색어 입력"
          }
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={handleKeyPress}
          className="border border-gray-300 rounded p-1"
        />
      )}
      <button
        onClick={onSearch}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        검색
      </button>
      {onClearSearch && (
        <button
          onClick={onClearSearch}
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          초기화
        </button>
      )}
    </div>
  );
}

export default SearchBar;
