import React, { useState } from "react";
import AdminSidebar from "./components/AdminSidebar.jsx";
import SearchBar from "./components/SearchBar";
import DataTable from "./components/DataTable";
import Pagination from "./components/Pagination";

function MembersPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("name");
  const [members, setMembers] = useState([
    { dept: "개발", name: "홍길동", id: 1, level: "사원", email: "hong@test.com", use_yn:"Y" },
    { dept: "영업", name: "김철수", id: 2, level: "대리", email: "kim@test.com", use_yn:"Y" },
  ]);
  const [currentPage, setCurrentPage] = useState(1);

  const columns = [
    { header: "부서", accessor: "dept" },
    { header: "이름", accessor: "name" },
    { header: "ID", accessor: "id" },
    { header: "직급", accessor: "level" },
    { header: "이메일", accessor: "email" },
    { header: "계정 활성 여부", accessor: "use_yn" },
  ];

  const searchOptions = [
    { value: "dept", label: "부서" },
    { value: "name", label: "이름" },
    { value: "id", label: "ID" },
    { value: "level", label: "직급" },
    { value: "email", label: "이메일" },
  ];

   const handleSearch = () => {
    console.log(`검색 유형: ${searchType}, 검색어: ${searchTerm}`);
    // TODO: searchType과 searchTerm을 활용해 API 호출 및 필터링 처리
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    // TODO: API 호출로 페이지 데이터 불러오기
  };

  return (
    <div className="flex">
      <AdminSidebar />
      <div className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-4">회원 관리</h1>
        <SearchBar
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          onSearch={handleSearch}
          searchType={searchType}
          setSearchType={setSearchType}
          searchOptions={searchOptions}
        />
        <DataTable columns={columns} data={members} />
        <Pagination
          currentPage={currentPage}
          totalPages={5}
          onPageChange={handlePageChange}
        />
      </div>
    </div>
  );
}

export default MembersPage;
