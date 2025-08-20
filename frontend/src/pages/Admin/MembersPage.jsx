import React from "react";
import axios from "axios";
import AdminSidebar from "./components/AdminSidebar.jsx";
import SearchBar from "./components/SearchBar";
import DataTable from "./components/DataTable";
import Pagination from "./components/Pagination";
import { useNavigate } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";

function MembersPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchType, setSearchType] = useState("name");
  const [members, setMembers] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const navigate = useNavigate();

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

  useEffect(() => {
    const fetchMembers = async () => {
      try {
        const response = await axios.get("/api/adminapp/users/");
        setMembers(response.data); // 백엔드에서 오는 JSON 데이터로 교체
      } catch (error) {
        console.error("회원 목록 불러오기 실패:", error);
      }
    };

    fetchMembers();
  }, []);

  //  const handleSearch = () => {
  //   try {
  //     const response = await axios.post("/api/adminapp/users/",{
  //       search_type: searchType,
  //       search_keyword: searchTerm,
  //     });

  //     setMembers(response.data.results || response.data);
  //     setCurrentPage(1);
  //   } catch (error) {
  //     console.error("")
  //   }
  // };

  const handleSearch = () => {
    console.log(`검색 유형: ${searchType}, 검색어: ${searchTerm}`);
    // TODO: searchType과 searchTerm을 활용해 API 호출 및 필터링 처리
  };


  const handlePageChange = (page) => {
    setCurrentPage(page);
    // TODO: API 호출로 페이지 데이터 불러오기
  };

  const handleGoToChat = useCallback(() => {
    navigate("/chat"); 
  }, [navigate]);

  return (
    <div className="flex">
      <AdminSidebar 
        onGoToChat={handleGoToChat}
      />
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
