import React, {useState} from "react";

import {LoadingSpinner, Tabs} from "hds-react";

import {useGetIndicesQuery} from "../../app/services";
import {ListPageNumbers, QueryStateHandler} from "../../common/components";
import {IIndex, IIndexResponse} from "../../common/models";

const Codes = (): JSX.Element => {
    const [filterParams] = useState({});
    return (
        <div className="view--codes">
            <h1 className="main-heading">Koodisto</h1>
            <Tabs>
                <Tabs.TabList>
                    <Tabs.Tab>Indeksit</Tabs.Tab>
                    <Tabs.Tab>Postinumerot</Tabs.Tab>
                    <Tabs.Tab>Laskentasäännöt</Tabs.Tab>
                    <Tabs.Tab>Rahoitusmuodot</Tabs.Tab>
                </Tabs.TabList>
                <Tabs.TabPanel>
                    <CodesResultList filterParams={filterParams} />
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Postinumerot</h2>
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Laskentasäännöt</h2>
                </Tabs.TabPanel>
                <Tabs.TabPanel>
                    <h2>Rahoitusmuodot</h2>
                </Tabs.TabPanel>
            </Tabs>
        </div>
    );
};

function result(data, error, isLoading, currentPage, setCurrentPage) {
    return (
        <div className="results">
            <QueryStateHandler
                data={data}
                error={error}
                isLoading={isLoading}
            >
                {!isLoading && data ? (
                    <>
                        <LoadedCodesResultsList data={data as IIndexResponse} />
                        <ListPageNumbers
                            currentPage={currentPage}
                            setCurrentPage={setCurrentPage}
                            pageInfo={data?.page}
                        />
                    </>
                ) : (
                    <LoadingSpinner />
                )}
            </QueryStateHandler>
        </div>
    );
}

const CodesResultList = ({filterParams}): JSX.Element => {
    const [currentPage, setCurrentPage] = useState(1);
    const {data: results, error, isLoading} = useGetIndicesQuery({...filterParams, page: currentPage});
    return result(results, error, isLoading, currentPage, setCurrentPage);
};
const CodesListItem = ({month, value}: IIndex) => {
    return (
        <div className="results-list__item results-list__item--code">
            <span className="month">{month}</span>
            <span className="value">{value}</span>
        </div>
    );
};
const LoadedCodesResultsList = ({data}: {data: IIndexResponse}) => {
    return (
        <>
            <div className="list-amount">{`Löytyi ${data.page.total_items}kpl tuloksia`}</div>
            <div className="list-headers">
                <div className="list-header month">Kuukausi</div>
                <div className="list-header value">Arvo</div>
            </div>
            <ul className="results-list">
                {data.contents.map((item: IIndex) => (
                    <CodesListItem
                        key={item.month}
                        month={item.month}
                        value={item.value}
                    />
                ))}
            </ul>
        </>
    );
};

export default Codes;
