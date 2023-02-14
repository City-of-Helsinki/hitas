import React from "react";

import {Button} from "hds-react";

import {PageInfo} from "../schemas";

interface ListPageNumbersProps {
    pageInfo: PageInfo | undefined;
    currentPage: number;
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
}

export default function ListPageNumbers({currentPage, setCurrentPage, pageInfo}: ListPageNumbersProps): JSX.Element {
    if (pageInfo === undefined) return <></>;

    const pageButtonData: {pageNumber: number; buttonText: string | number}[] = [];
    const totalPages = pageInfo.total_pages;
    for (let i = -3; i <= 3; i++) {
        if (currentPage + i > 0 && currentPage + i <= totalPages) {
            pageButtonData.push({pageNumber: currentPage + i, buttonText: currentPage + i});
        }
    }
    pageButtonData.unshift({pageNumber: Math.max(1, currentPage - 1), buttonText: "<"});
    pageButtonData.push({pageNumber: Math.min(totalPages, currentPage + 1), buttonText: ">"});
    if (totalPages === 1) return <></>;
    return (
        <div style={{display: "flex", justifyContent: "space-between"}}>
            {pageButtonData.map(({pageNumber, buttonText}) => (
                <Button
                    key={`pageButton__${buttonText}`}
                    onClick={() => setCurrentPage(pageNumber)}
                    style={{
                        backgroundColor: "transparent",
                        color: "var(--text-color)",
                        border: "0",
                        fontWeight: "bold",
                    }}
                >
                    {buttonText}
                </Button>
            ))}
        </div>
    );
}
