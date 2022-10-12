import React, {useState} from "react";

import {Button, Combobox, IconPlus, IconSearch, LoadingSpinner, Tabs} from "hds-react";

import {useGetIndicesQuery} from "../../app/services";
import {FilterTextInputField, ListPageNumbers} from "../../common/components";
import {IIndex, IIndexResponse} from "../../common/models";

const indices = [
    {label: "max-price-index"},
    {label: "market-price-index"},
    {label: "construction-price-index"},
    {label: "construction-price-index-pre-2005"},
    {label: "surface-area-price-ceiling"},
];
const getIndexName = (state: string) => {
    switch (state) {
        case "max-price-index":
            return "Enimmäishintaindeksi";
        case "market-price-index":
            return "Markkinahintaindeksi";
        case "construction-price-index":
            return "Rakennushintaindeksi";
        case "construction-price-index-pre-2005":
            return "Rakennushintaindeksi (ennen 2005)";
        case "surface-area-price-ceiling":
            return "Rajaneliöhinta";
        default:
            return "VIRHE";
    }
};
const indexOptions = indices.map(({label}) => {
    return {label: getIndexName(label), value: label};
});
const Codes = (): JSX.Element => {
    const [filterParams, setFilterParams] = useState({name: ""});
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
                <Tabs.TabPanel className="view--codes__tab--indices">
                    <CodesResultList
                        filterParams={filterParams}
                        setFilterParams={setFilterParams}
                    />
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
const CodesResultList = ({filterParams, setFilterParams}): JSX.Element => {
    const [currentPage, setCurrentPage] = useState(1);
    const [currentIndex, setCurrentIndex] = useState();
    const {
        data: results,
        error,
        isLoading,
    } = useGetIndicesQuery({
        ...filterParams,
        page: currentPage,
        indexType: indices[0].label,
    });
    return result(
        results,
        error,
        isLoading,
        currentPage,
        setCurrentPage,
        currentIndex,
        setCurrentIndex,
        filterParams,
        setFilterParams
    );
};

function result(
    data,
    error,
    isLoading,
    currentPage,
    setCurrentPage,
    currentIndex,
    setCurrentIndex,
    filterParams,
    setFilterParams
) {
    const onSelectionChange = (value: {value: string}) => {
        setCurrentIndex(value.value);
    };
    return !isLoading ? (
        <div className="listing">
            <div className="search">
                <FilterTextInputField
                    label=""
                    filterFieldName="display_name"
                    filterParams={filterParams}
                    setFilterParams={setFilterParams}
                />
                <IconSearch />
            </div>
            <LoadedCodesResultsList data={data as IIndexResponse} />
            <ListPageNumbers
                currentPage={currentPage}
                setCurrentPage={setCurrentPage}
                pageInfo={data?.page}
            />
            <div className="filters">
                <Combobox
                    label={"Indeksi"}
                    options={indexOptions}
                    toggleButtonAriaLabel={"Toggle menu"}
                    onChange={onSelectionChange}
                    clearable
                />
            </div>
        </div>
    ) : (
        <LoadingSpinner />
    );
}

const LoadedCodesResultsList = ({data}: {data: IIndexResponse}) => {
    return (
        <div className="results">
            <div className="list-amount">{`Löytyi ${data.page.total_items}kpl tuloksia`}</div>
            <div className="list-headers">
                <div className="list-header month">Kuukausi</div>
                <div className="list-header value">Arvo</div>
            </div>
            <ul className="results-list">
                <CodesListItem
                    month={"2022-01"}
                    value={127.12}
                />
                <CodesListItem
                    month={"2022-02"}
                    value={194.44}
                />
                <CodesListItem
                    month={"2022-01"}
                    value={127.12}
                />
                <CodesListItem
                    month={"2022-02"}
                    value={194.44}
                />
                <CodesListItem
                    month={"2022-01"}
                    value={127.12}
                />
                <CodesListItem
                    month={"2022-02"}
                    value={194.44}
                />
                {data.contents.map((item: IIndex) => (
                    <CodesListItem
                        key={item.month}
                        month={item.month}
                        value={item.value}
                    />
                ))}
            </ul>
            <Button
                theme="black"
                iconLeft={<IconPlus />}
            >
                Lisää indeksi
            </Button>
        </div>
    );
};
const CodesListItem = ({month, value}: IIndex) => {
    return (
        <div className="results-list__item results-list__item--code">
            <span className="month">{month}</span>
            <span className="value">{value}</span>
        </div>
    );
};

export default Codes;
