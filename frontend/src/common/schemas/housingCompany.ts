import {boolean, number, object, string, z} from "zod";
import {AddressSchema, APIIdString, CodeSchema, PageInfoSchema} from "./common";
import {housingCompanyHitasTypes, housingCompanyRegulationStatus} from "./enums";
import {ImprovementSchema, MarketPriceIndexImprovementSchema} from "./improvements";
import {PropertyManagerSchema} from "./propertyManager";
import {DocumentSchema} from "./document";

// ********************************
// * Building
// ********************************

const BuildingSchema = object({
    id: APIIdString,
    address: AddressSchema,
    building_identifier: string().nullable(),
    apartment_count: number(),
});
export type IBuilding = z.infer<typeof BuildingSchema>;

export const WritableBuildingSchema = object({
    id: APIIdString.optional(),
    address: object({street_address: string()}),
    building_identifier: string().nullable(),
    real_estate_id: APIIdString.nullable(),
});
export type IBuildingWritable = z.infer<typeof WritableBuildingSchema>;

// ********************************
// * Real Estate
// ********************************

const RealEstateSchema = object({
    id: APIIdString,
    property_identifier: string(),
    address: AddressSchema,
    buildings: BuildingSchema.array(),
});
export type IRealEstate = z.infer<typeof RealEstateSchema>;

export const WritableRealEstateSchema = object({
    id: APIIdString.optional(),
    property_identifier: string(),
});

// ********************************
// * Housing Company Fields
// ********************************

const HousingCompanyAreaSchema = object({name: string(), cost_area: number()});

const HousingCompanyHitasTypeSchema = z.enum(housingCompanyHitasTypes);

export const HousingCompanyRegulationStatusSchema = z.enum(housingCompanyRegulationStatus);

const HousingCompanyStateSchema = object({
    status: string(),
    housing_company_count: number(),
    apartment_count: number(),
});
export type IHousingCompanyState = z.infer<typeof HousingCompanyStateSchema>;

// ********************************
// * Housing Company
// ********************************

export const HousingCompanySchema = object({
    id: APIIdString,
    name: string(),
    hitas_type: HousingCompanyHitasTypeSchema,
    exclude_from_statistics: boolean(),
    regulation_status: HousingCompanyRegulationStatusSchema,
    over_thirty_years_old: boolean(),
    completed: boolean(),
    address: AddressSchema,
    area: HousingCompanyAreaSchema,
    completion_date: string().nullable(),
});
export type IHousingCompany = z.infer<typeof HousingCompanySchema>;

export const HousingCompanyOwnerSchema = object({
    number: number(),
    surface_area: number(),
    share_numbers: string(),
    purchase_date: string(),
    owner_name: string(),
    owner_ssn: string(),
    owner_id: APIIdString,
});
export type IHousingCompanyOwner = z.infer<typeof HousingCompanyOwnerSchema>;

export const HousingCompanyDetailsSchema = object({
    id: APIIdString,
    business_id: string().nullable(),
    name: object({official: string(), display: string()}),
    hitas_type: HousingCompanyHitasTypeSchema,
    new_hitas: boolean(),
    exclude_from_statistics: boolean(),
    regulation_status: HousingCompanyRegulationStatusSchema,
    over_thirty_years_old: boolean(),
    completed: boolean(),
    address: AddressSchema,
    area: HousingCompanyAreaSchema,
    completion_date: string().nullable(),
    real_estates: RealEstateSchema.array(),
    building_type: CodeSchema,
    developer: CodeSchema,
    property_manager: PropertyManagerSchema.nullable(),
    property_manager_changed_at: string().optional(),
    acquisition_price: number(),
    primary_loan: number().optional(),
    sales_price_catalogue_confirmation_date: string().nullable(),
    notes: string().nullable(),
    archive_id: number(),
    release_date: string().nullable(),
    legacy_release_date: string().nullable(),
    last_modified: object({
        user: object({
            user: string().nullable(),
            first_name: string().nullable(),
            last_name: string().nullable(),
        }),
        datetime: z.date(),
    }),
    summary: object({
        average_price_per_square_meter: number(),
        realized_acquisition_price: number(),
        total_shares: number(),
        total_surface_area: number(),
    }),
    improvements: object({
        market_price_index: MarketPriceIndexImprovementSchema.array(),
        construction_price_index: ImprovementSchema.array(),
    }),
    documents: DocumentSchema.array(),
});
export type IHousingCompanyDetails = z.infer<typeof HousingCompanyDetailsSchema>;

export const HousingCompanyWritableSchema = HousingCompanyDetailsSchema.pick({
    name: true,
    business_id: true,
    hitas_type: true,
    exclude_from_statistics: true,
    regulation_status: true,
    legacy_release_date: true,
    address: true,
    acquisition_price: true,
    primary_loan: true,
    sales_price_catalogue_confirmation_date: true,
    notes: true,
    improvements: true,
}).merge(
    object({
        id: APIIdString.optional(),
        building_type: object({id: string()}),
        developer: object({id: string()}),
        property_manager: object({id: string().optional()}).nullable(),
    })
);
export type IHousingCompanyWritable = z.infer<typeof HousingCompanyWritableSchema>;

// ********************************
// * Sales Catalog
// ********************************

export const SalesCatalogApartmentSchema = object({
    row: number(),
    stair: string(),
    floor: string(),
    apartment_number: number(),
    rooms: number(),
    apartment_type: string().or(
        object({
            id: string(),
            value: string(),
        })
    ),
    surface_area: number(),
    share_number_start: number(),
    share_number_end: number(),
    catalog_purchase_price: number(),
    catalog_primary_loan_amount: number(),
    acquisition_price: number(),
});
export type ISalesCatalogApartment = z.infer<typeof SalesCatalogApartmentSchema>;

// ********************************
// * API
// ********************************

export const HousingCompanyApartmentQuerySchema = object({
    housingCompanyId: string(),
    params: object({
        page: number(),
    }),
});
export type IHousingCompanyApartmentQuery = z.infer<typeof HousingCompanyApartmentQuerySchema>;

export const HousingCompanyListResponseSchema = object({
    page: PageInfoSchema,
    contents: HousingCompanySchema.array(),
});
export type IHousingCompanyListResponse = z.infer<typeof HousingCompanyListResponseSchema>;
