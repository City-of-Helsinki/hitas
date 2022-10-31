import React from "react";

interface PageCounterProps {
    currentPage: number;
    totalPages: number;
}

const PageCounter = ({currentPage, totalPages}: PageCounterProps) => {
    if (totalPages <= 1) return <></>;
    return (
        <div className={"results__page-counter"}>
            Sivu {currentPage} / {totalPages}
        </div>
    );
};

export default PageCounter;
