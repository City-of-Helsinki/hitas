// Common Fields

export interface IAddress {
    street_address: string;
    postal_code: string;
    readonly city?: string; // Always returned when reading, but not required when writing
}

export interface IImprovement {
    name: string;
    value: number;
    completion_date: string;
}

// Housing Company

// Housing Company Fields

interface IHousingCompanyArea {
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
type IHousingCompanyState = typeof HousingCompanyStates[number];

interface IHousingCompanyDetailsName {
    official: string;
    display: string;
}

// // Housing Company Models

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
    real_estates: IRealEstate[];
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

// Real Estate

export interface IRealEstate {
    readonly id?: string;
    property_identifier: string;
    address: IAddress;
    buildings: IBuilding[];
}

// Building

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

// Apartment

// // Apartment Fields

export interface IApartmentAddress {
    street_address: string;
    readonly postal_code?: string;
    readonly city?: string; // Always returned when reading, but not required when writing
    apartment_number: number;
    floor: string | null;
    stair: string | null;
}

interface IApartmentLinkedModel {
    readonly id: string;
    readonly link: string;
}

interface IApartmentLinkedModels {
    readonly housing_company: IApartmentLinkedModel & {display_name: string};
    readonly real_estate: IApartmentLinkedModel;
    readonly building: IApartmentLinkedModel & {street_address: string};
    readonly apartment: IApartmentLinkedModel;
}

export interface IApartmentUnconfirmedMaximumPrice {
    maximum: boolean;
    value: number;
}

interface IApartmentUnconfirmedMaximumPriceIndices {
    construction_price_index: IApartmentUnconfirmedMaximumPrice;
    market_price_index: IApartmentUnconfirmedMaximumPrice;
    surface_area_price_ceiling: IApartmentUnconfirmedMaximumPrice;
}

export type IApartmentConfirmedMaximumPrice = {
    id: string | null;
    calculation_date: string;
    confirmed_at: string;
    created_at: string;
    maximum_price: number;
    valid: {
        is_valid: boolean;
        valid_until: string;
    };
} | null;

interface IApartmentPrices {
    readonly acquisition_price: number | null;

    debt_free_purchase_price: number | null;
    purchase_price: number | null;
    primary_loan_amount: number | null;

    first_purchase_date: string | null;
    latest_purchase_date: string | null;

    construction: {
        loans: number | null;
        additional_work: number | null;
        interest: number | null;
        debt_free_purchase_price: number | null;
    };

    maximum_prices: {
        confirmed: IApartmentConfirmedMaximumPrice;
        unconfirmed: {
            onwards_2011: IApartmentUnconfirmedMaximumPriceIndices;
            pre_2011: IApartmentUnconfirmedMaximumPriceIndices;
        };
    };
}

export const ApartmentStates = ["free", "reserved", "sold"] as const;
export type ApartmentState = typeof ApartmentStates[number];

export type IApartmentConstructionPriceIndexImprovement = IImprovement & {
    depreciation_percentage: number; // 0.0 | 2.5 | 10.0
};

type IApartmentShares = {
    start: number;
    end: number;
    readonly total: number;
} | null;

// // Apartment Models

export interface IApartment {
    readonly id: string;
    state: ApartmentState;
    type: string;
    surface_area: number;
    rooms: number | null;
    address: IApartmentAddress;
    completion_date: string | null;
    housing_company: string;
    ownerships: IOwnership[];
    readonly links: IApartmentLinkedModels;
}

export interface IApartmentDetails {
    readonly id: string;
    state: ApartmentState;
    type: ICode;
    surface_area: number;
    rooms: number | null;
    shares: IApartmentShares;
    address: IApartmentAddress;
    prices: IApartmentPrices;
    completion_date: string | null;
    ownerships: IOwnership[];
    notes: string;
    improvements: {
        market_price_index: IImprovement[];
        construction_price_index: IApartmentConstructionPriceIndexImprovement[];
    };
    readonly links: IApartmentLinkedModels;
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
    prices: Omit<IApartmentPrices, "maximum_prices" | "acquisition_price">;
    completion_date?: string | null;
    building: string;
    ownerships: IOwnership[];
    notes: string;
    improvements: {
        market_price_index: IImprovement[];
        construction_price_index: IApartmentConstructionPriceIndexImprovement[];
    };
}

// Maximum Price

// //  Maximum Price Fields

interface ICalculation {
    maximum_price: number;
    valid_until: string;
    maximum: boolean;
}

interface IIndexCalculationVariables {
    calculation_variables: {
        acquisition_price: number;
        additional_work_during_construction: number;
        basic_price: number;
        index_adjustment: number;
        apartment_improvements: number;
        housing_company_improvements: number;
        debt_free_price: number;
        debt_free_price_m2: number;
        apartment_share_of_housing_company_loans: number;
        completion_date: string;
        completion_date_index: number;
        calculation_date: string;
        calculation_date_index: number;
    };
}

// // Maximum Price Models

export interface IApartmentMaximumPrice {
    readonly id: string;
    created_at: string;
    confirmed_at: string | null;
    maximum_price: number;
    calculation_date: string;
    valid_until: string;
    index: string;
    calculations: {
        construction_price_index: ICalculation & IIndexCalculationVariables;
        market_price_index: ICalculation & IIndexCalculationVariables;
        surface_area_price_ceiling: ICalculation & {
            calculation_variables: {
                calculation_date: string;
                calculation_date_value: number;
                surface_area: number;
            };
        };
    };
    apartment: {
        address: IApartmentAddress;
        type: string;
        ownerships: IOwnership[];
        rooms: number | null;
        shares: IApartmentShares;
        surface_area: number;
    };
    housing_company: {
        archive_id: number;
        official_name: string;
        property_manager: {
            name: string;
            street_address: string;
        };
    };
}

export interface IApartmentMaximumPriceWritable {
    calculation_date: string | null;
    apartment_share_of_housing_company_loans: number | null;
    apartment_share_of_housing_company_loans_date: string | null;
    additional_info: string;
}

// Indices

export interface IIndex {
    indexType: string;
    month: string;
    value: number | null;
}

// Other models

export interface ICode {
    readonly id: string;
    value: string;
    description: string | null;
    code: string;
}

export interface IPostalCode {
    value: string;
    city: string;
    cost_area: 1 | 2 | 3 | 4;
}

export interface IPropertyManager {
    readonly id: string;
    name: string;
    email: string;
    address: IAddress;
}

export interface IOwner {
    readonly id?: string;
    name: string;
    identifier: string | null;
    email: string | null;
}

export interface IOwnership {
    owner: IOwner;
    percentage: number;
    start_date?: string | null;
    end_date?: string | null;
}

// Requests / Responses

// // General

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

// // LIST Responses

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

// // Query Parameters

export interface IHousingCompanyApartmentQuery {
    housingCompanyId: string;
    params: {
        page: number;
    };
}

export interface IApartmentQuery {
    housingCompanyId: string;
    apartmentId: string;
}

export interface IIndexQuery {
    indexType: string;
    params: {
        page: number;
        limit: number;
        year: string;
    };
}
