export interface IAddress {
    street_address: string;
    postal_code: string;
    city?: string; // Always returned when reading, but not required when writing
}

export interface ICode {
    readonly id: string;
    value: string;
    description: string | null;
    code: string;
}

export interface IApartmentConstructionPriceIndexImprovement {
    name: string;
    value: number;
    completion_date: string;
    depreciation_percentage: number; // 0.0 | 2.5 | 10.0
}

export interface IImprovement {
    name: string;
    value: number;
    completion_date: string;
}

export interface IHousingCompany {
    readonly id: string;
    name: string;
    state: IHousingCompanyState;
    address: IAddress;
    area: IHousingCompanyArea;
    date: string | null;
}

export interface IHousingCompanyDetails {
    readonly id: string;
    name: IHousingCompanyDetailsName;
    business_id: string | null;
    state: IHousingCompanyState;
    address: IAddress;
    area: IHousingCompanyArea;
    date: string | null;
    financing_method: ICode;
    building_type: ICode;
    developer: ICode;
    property_manager: IPropertyManager | null;
    acquisition_price: number;
    primary_loan: number | null;
    sales_price_catalogue_confirmation_date: string | null;
    notification_date: string | null;
    archive_id: number;
    notes: string | null;
    last_modified: {
        user: {
            user: string | null;
            first_name: string | null;
            last_name: string | null;
        };
        datetime: Date;
    };
    real_estates: Array<IRealEstate>;
    summary: {
        average_price_per_square_meter: number;
        realized_acquisition_price: number;
        total_shares: number;
        total_surface_area: number;
    };
    improvements: {
        market_price_index: IImprovement[];
        construction_price_index: IImprovement[];
    };
}

export interface IHousingCompanyWritable {
    readonly id?: string;
    name: IHousingCompanyDetailsName;
    business_id: string | null;
    state: IHousingCompanyState;
    address: IAddress;
    financing_method: {id: string};
    building_type: {id: string};
    developer: {id: string};
    property_manager: {id: string} | null;
    acquisition_price: number;
    primary_loan: number | null;
    sales_price_catalogue_confirmation_date: string | null;
    notes: string | null;
    improvements: {
        market_price_index: IImprovement[];
        construction_price_index: IImprovement[];
    };
}

export interface IHousingCompanyArea {
    name: string;
    cost_area: number;
}

export const HousingCompanyStates = [
    "not_ready",
    "lt_30_years",
    "gt_30_years_not_free",
    "gt_30_years_free",
    "gt_30_years_plot_department_notification",
    "half_hitas",
    "ready_no_statistics",
] as const;

export type IHousingCompanyState = typeof HousingCompanyStates[number];

export interface IHousingCompanyDetailsName {
    official: string;
    display: string;
}

export interface IRealEstate {
    readonly id?: string;
    property_identifier: string;
    address: IAddress;
    buildings: Array<IBuilding>;
}

export interface IBuilding {
    readonly id?: string;
    address: IAddress;
    completion_date: string | null;
    building_identifier: string | null;
}

export interface IBuildingWritable {
    readonly id?: string;
    address: {street_address: string};
    building_identifier: string | null;
    real_estate_id: string | null;
}

export interface IApartmentAddress {
    street_address: string;
    readonly postal_code?: string;
    readonly city?: string; // Always returned when reading, but not required when writing
    apartment_number: number;
    floor: string | null;
    stair: string | null;
}

export interface IApartmentLink {
    id: string;
    link: string;
    display_name?: string;
}

export interface IApartmentLinks {
    housing_company: IApartmentLink;
    real_estate: IApartmentLink;
    building: IApartmentLink;
    apartment: IApartmentLink;
}

export interface IApartment {
    readonly id: string;
    state: ApartmentState;
    links: IApartmentLinks;
    type: string;
    surface_area: number;
    rooms: number | null;
    address: IApartmentAddress;
    completion_date: string | null;
    housing_company: string;
    ownerships: Array<IOwnership>;
}

export interface IApartmentConstructionPrices {
    loans: number | null;
    additional_work: number | null;
    interest: number | null;
    debt_free_purchase_price: number | null;
}

export interface IApartmentPrices {
    debt_free_purchase_price: number | null;
    purchase_price: number | null;
    primary_loan_amount: number | null;

    first_purchase_date: string | null;
    latest_purchase_date: string | null;

    construction: IApartmentConstructionPrices;
}

export interface IHousingCompanyApartmentQuery {
    housingCompanyId: string;
    params: object;
}

export interface IApartmentQuery {
    housingCompanyId: string;
    apartmentId: string;
}

export const ApartmentStates = ["free", "reserved", "sold"] as const;

export type ApartmentState = typeof ApartmentStates[number];

export interface IApartmentDetails {
    readonly id: string;
    state: ApartmentState;
    type: ICode;
    surface_area: number;
    rooms: number | null;
    shares: {
        start: number;
        end: number;
        readonly total: number;
    } | null;
    links: {
        housing_company: ILinkedModel & {display_name: string};
        real_estate: ILinkedModel;
        building: ILinkedModel & {street_address: string};
        apartment: ILinkedModel;
    };
    address: IApartmentAddress;
    prices: IApartmentPrices;
    completion_date: string | null;
    ownerships: IOwnership[];
    notes: string;
    improvements: {
        market_price_index: IImprovement[];
        construction_price_index: IApartmentConstructionPriceIndexImprovement[];
    };
}

export interface IApartmentWritable {
    readonly id?: string;
    state: ApartmentState | null;
    type: {id: string};
    surface_area: number | null;
    rooms: number | null;
    shares: {
        start: number | null;
        end: number | null;
    };
    address: Omit<IApartmentAddress, "apartment_number"> & {apartment_number: number | null};
    prices: IApartmentPrices;
    completion_date?: string | null;
    building: string;
    ownerships: IOwnership[];
    notes: string;
    improvements: {
        market_price_index: IImprovement[];
        construction_price_index: IApartmentConstructionPriceIndexImprovement[];
    };
}

export interface IPropertyManager {
    readonly id: string;
    name: string;
    email: string;
    address: IAddress;
}

export interface IOwner {
    readonly id: string;
    name: string;
    identifier: string | null;
    email: string | null;
    address: IAddress;
}

export interface IOwnership {
    owner: IOwner;
    percentage: number;
    start_date?: string | null;
    end_date?: string | null;
}

// Non-model data

export interface ILinkedModel {
    id: string;
    link: string;
}

export interface PageInfo {
    size: number;
    total_items: number;
    current_page: number;
    total_pages: number;
    links: {
        next: string | null;
        previous: string | null;
    };
}

export interface IPostalCode {
    value: string;
    city: string;
    cost_area: 1 | 2 | 3 | 4;
}

export interface IIndex {
    indexType: string;
    month: string;
    value: number | null;
}

export interface IIndexQuery {
    indexType: string;
    params?: object;
}

// List response interfaces

export interface IHousingCompanyListResponse {
    page: PageInfo;
    contents: IHousingCompany[];
}

export interface IApartmentListResponse {
    page: PageInfo;
    contents: IApartment[];
}

export interface ICodeResponse {
    page: PageInfo;
    contents: ICode[];
}

export interface IPostalCodeResponse {
    page: PageInfo;
    contents: IPostalCode[];
}

export interface IIndexResponse {
    page: PageInfo;
    contents: IIndex[];
}
