import React from "react";

import {Pagination} from "hds-react";

import {PageInfo} from "../schemas";

interface ListPageNumbersProps {
    pageInfo: PageInfo;
    currentPage: number;
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
}

export default function ListPageNumbers({
    currentPage,
    setCurrentPage,
    pageInfo,
    pageInfo: {total_pages: totalPages},
}: ListPageNumbersProps): React.JSX.Element {
    if (pageInfo === undefined || totalPages === 1) return <></>;
    return (
        <Pagination
            language="fi"
            onChange={(event, index) => {
                event.preventDefault();
                setCurrentPage(index + 1);
            }}
            pageCount={totalPages}
            pageHref={() => currentPage.toString()}
            pageIndex={currentPage - 1}
            paginationAriaLabel="Pagination"
            siblingCount={2}
            hideNextButton={currentPage === totalPages}
            hidePrevButton={currentPage === 1}
        />
    );
}
