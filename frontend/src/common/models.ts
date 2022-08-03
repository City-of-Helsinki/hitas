export interface IAddress {
    street: string;
    postal_code: string;
    city: string;
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
    financing_method?: ICode;
    building_type?: ICode;
    developer?: ICode;
    property_manager?: IPropertyManager;
    acquisition_price?: IHousingCompanyDetailsAcquisitionPrice;
    primary_loan?: number | null;
    sales_price_catalogue_confirmation_date?: string | null;
    notification_date?: string | null;
    legacy_id?: string | null;
    notes?: string | null;
    last_modified?: IHousingCompanyDetailsLastModified;
    real_estates: Array<IRealEstate>;
}

export interface IHousingCompanyArea {
    name: string;
    cost_area: number;
}

export type IHousingCompanyState =
    | "not_ready"
    | "lt_30_years"
    | "gt_30_years_not_free"
    | "gt_30_years_free"
    | "gt_30_years_plot_department_notification"
    | "half_hitas"
    | "ready_no_statistics";

export interface IHousingCompanyDetailsName {
    official: string;
    display: string;
}

export interface IHousingCompanyDetailsLastModifiedUser {
    user?: string | null;
    first_name: string | null;
    last_name: string | null;
}

export interface IHousingCompanyDetailsLastModified {
    user: IHousingCompanyDetailsLastModifiedUser;
    datetime: Date;
}

export interface IHousingCompanyDetailsAcquisitionPrice {
    initial: number;
    realized: number | null;
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
    building_identifier?: string | null;
}

export interface IApartment {
    readonly id: string;
    state: ApartmentState;
    apartment_type: string;
    surface_area: number;
    address: IAddress;
    apartment_number: number;
    stair: string;
    date: string | null;
    housing_company: string;
    owners: Array<IOwner>;
}

export interface IApartmentDetails {
    readonly id: string;
    state: ApartmentState;
    apartment_type: ICode;
    surface_area: number;
    share_number_start?: number | null;
    share_number_end?: number | null;
    address: IAddress;
    apartment_number: number;
    floor?: number;
    stair?: string;
    date: string | null;
    debt_free_purchase_price?: number | null;
    purchase_price?: number | null;
    acquisition_price?: number | null;
    primary_loan_amount?: number | null;
    loans_during_construction?: number | null;
    interest_during_construction?: number | null;
    building?: string;
    real_estate?: string;
    housing_company: IHousingCompany;
    owners: Array<IOwner>;
    notes?: string | null;
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

export interface IOwner {
    person: IPerson;
    ownership_percentage: number;
    ownership_start_date: string | null;
    ownership_end_date: string | null;
}

export interface PageInfo {
    size: number;
    total_items: number;
    current_page: number;
    total_pages: number;
    links: PageInfoLinks;
}

export interface PageInfoLinks {
    next?: string | null;
    previous?: string | null;
}
