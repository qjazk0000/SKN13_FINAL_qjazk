import React from "react";

function SearchBar({ 
    searchTerm, 
    setSearchTerm, 
    onSearch, 
    searchType, 
    setSearchType,
    searchOptions = []  
}) {
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
      <input
        type="text"
        placeholder={
          searchOptions.find(opt => opt.value === searchType)?.label + " 입력" || "검색어 입력"
        }
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="border border-gray-300 rounded p-2 flex-1"
      />
      <button
        onClick={onSearch}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        검색
      </button>
    </div>
  );
}

export default SearchBar;
