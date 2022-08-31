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
    business_id: string;
    state: IHousingCompanyState;
    address: IAddress;
    area: IHousingCompanyArea;
    date: string | null;
    financing_method: ICode;
    building_type: ICode;
    developer: ICode;
    property_manager: IPropertyManager;
    acquisition_price: {
        initial: number;
        realized: number | null;
    };
    primary_loan: number | null;
    sales_price_catalogue_confirmation_date: string | null;
    notification_date: string | null;
    legacy_id: string | null;
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
}

export interface IHousingCompanyWritable {
    readonly id?: string;
    name: IHousingCompanyDetailsName;
    business_id: string;
    state: IHousingCompanyState;
    address: IAddress;
    financing_method: {id: string};
    building_type: {id: string};
    developer: {id: string};
    property_manager: {id: string};
    acquisition_price: {
        initial: number | null;
        realized: number | null;
    };
    primary_loan: number | null;
    sales_price_catalogue_confirmation_date: string | null;
    notes: string | null;
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
    readonly id: string;
    property_identifier: string;
    address: IAddress;
    buildings: Array<IBuilding>;
}

export interface IBuilding {
    readonly id: string;
    address: IAddress;
    completion_date: string | null;
    building_identifier: string | null;
}

export interface IApartment {
    readonly id: string;
    state: ApartmentState;
    apartment_type: string;
    surface_area: number;
    address: IAddress;
    apartment_number: number;
    stair: string;
    completion_date: string | null;
    housing_company: string;
    ownerships: Array<IOwnership>;
}

export interface IApartmentConstructionPrices {
    loans: number;
    additional_work: number;
    interest: number;
    debt_free_purchase_price: number;
}

export interface IApartmentPrices {
    debt_free_purchase_price: number;
    primary_loan_amount: number;
    acquisition_price: number;
    purchase_price: number;

    first_purchase_date: string | null;
    second_purchase_date: string | null;

    construction: IApartmentConstructionPrices;
}

export interface IApartmentDetails {
    readonly id: string;
    state: ApartmentState;
    apartment_type: ICode;
    surface_area: number;
    shares: {
        start: number;
        end: number;
        readonly total: number;
    };
    address: IAddress;
    apartment_number: number;
    floor: number;
    stair: string;
    completion_date: string | null;
    prices: IApartmentPrices;
    building: string;
    real_estate: string;
    housing_company: IHousingCompany;
    ownerships: Array<IOwnership>;
    notes: string;
}

export type ApartmentState = "free" | "reserved" | "sold";

export interface IPropertyManager {
    readonly id: string;
    name: string;
    email: string;
    address: IAddress;
}

export interface IPerson {
    readonly id: string;
    first_name: string;
    last_name: string;
    social_security_number: string | null;
    email: string | null;
    address: IAddress;
}

export interface IOwnership {
    owner: IPerson;
    percentage: number;
    start_date: string | null;
    end_date: string | null;
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
