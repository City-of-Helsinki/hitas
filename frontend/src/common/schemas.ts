import {array, boolean, literal, number, object, string, z} from "zod";

// ********************************
// * Enumerations
// ********************************

export const housingCompanyHitasTypes = [
    "non_hitas",
    "hitas_1",
    "hitas_2",
    "hitas_1_no_interest",
    "hitas_2_no_interest",
    "new_hitas_1",
    "new_hitas_2",
    "half_hitas",
    "rental_hitas_1",
    "rental_hitas_2",
] as const;

export const housingCompanyRegulationStatus = [
    "regulated",
    "released_by_hitas",
    "released_by_plot_department",
] as const;

export const hitasQuarters = [
    {
        value: "02-01",
        label: "1.2. - 30.4.",
    },
    {
        value: "05-01",
        label: "1.5. - 31.7.",
    },
    {
        value: "08-01",
        label: "1.8. - 31.10.",
    },
    {
        value: "11-01",
        label: "1.11. - 31.1.",
    },
];

export const indexNames = ["market_price_index", "construction_price_index", "surface_area_price_ceiling"] as const;

const CostAreas = ["1", "2", "3", "4"] as const;

// ********************************
// * Error messages
// ********************************

export const errorMessages = {
    required: "Pakollinen kenttä",
    postalCodeFormat: "Virheellinen postinumero",
    stringLength: "Liian lyhyt arvo",
    stringMin: "Liian lyhyt arvo",
    stringMax: "Liian monta merkkiä",
    stringMaxIs: "Maksimimerkkimäärä on ",
    numberLength: "Liian lyhyt arvo",
    numberType: "Arvon pitää olla numero",
    numberMin: "Liian pieni arvo",
    numberMax: "Liian suuri arvo",
    numberPositive: "Arvon täytyy olla positiivinen luku",
    dateFormat: "Virheellinen päivämäärä",
    dateMin: "Liian aikainen päivämäärä",
    dateMax: "Liian myöhäinen päivämäärä",
    noOwnerships: "Asunnolla täytyy olla omistaja",
    ownershipPercent: "Asunnon omistajuusprosentin tulee olla yhteensä 100%",
    ownershipDuplicate: "Samaa henkilöä ei voi valita useaan kertaan",
    priceMin: "Kauppahinta ei saa olla tyhjä",
    priceMax: "Kauppahinta ei saa ylittää 999 999 €",
    loanShareMin: "Lainaosuus ei voi olla alle 0 €",
    emailInvalid: "Virheellinen sähköpostiosoite",
    urlInvalid: "Virheellinen www-osoite",
    APIIdMin: "Rajapinnan palauttamassa ID-arvossa liian vähän merkkejä",
    APIIdMax: "Rajapinnan palauttamassa ID-arvossa on liian monta merkkiä",
    overMaxPrice: "Kauppahinta ylittää enimmäishinnan",
    priceHigherThanUnconfirmedMaxPrice: "Velaton kauppahinta ylittää rajaneliöhinnan.",
    loanShareChanged: "Lainaosuus muuttunut laskelmasta",
    loanShareChangedCatalog: "Lainaosuus muuttunut myyntihintaluettelon tiedoista",
    catalogOverMaxPrice: "Kauppahinta ylittää myyntihintaluettelon hinnan",
    catalogUnderMaxPrice: "Kauppahinta alittaa myyntihintaluettelon hinnan",
    catalogPricesMissing: "Myyntihintaluettelon hinnat puuttuvat",
    sharesEmpty: "Toinen osakekenttä on tyhjä",
    sharesStartGreaterThanEnd: "Osakkeiden lopun on oltava suurempi kuin alun",
    constructionInterestEmpty: "Toinen korkokenttä on tyhjä",
    constructionInterest6GreaterThan14: "14% koron on oltava suurempi kuin 6% koron",
    maxTwoDecimalPlaces: "Anna arvo enintän kahden desimaalin tarkkuudella",
    noDecimalPlaces: "Anna arvo kokonaislukuna",
};

const customErrorMap: z.ZodErrorMap = (issue, ctx) => {
    let returnValue = {message: ctx.defaultError};
    if (issue.code === z.ZodIssueCode.invalid_type) {
        if (issue.expected === "number") {
            returnValue = {message: errorMessages.numberType};
        }
    }
    if (issue.code === z.ZodIssueCode.too_small || issue.code === z.ZodIssueCode.too_big) {
        const isMin = issue.code === z.ZodIssueCode.too_small;
        if (issue.type !== "set" && issue.type !== "array") {
            returnValue = {
                message: `${errorMessages[`${issue.type + isMin ? "Min" : "Max"}`]} (${
                    isMin ? `min ${issue.minimum}` : `max ${issue.maximum}`
                })`,
            };
        }
    }
    if (issue.code === z.ZodIssueCode.invalid_string) {
        if (issue.validation !== "uuid") {
            returnValue = {message: errorMessages[`${issue.validation}Invalid`]};
        }
    }
    if (issue.code === z.ZodIssueCode.invalid_date) {
        returnValue = {message: errorMessages.dateFormat};
    }
    return returnValue;
};

z.setErrorMap(customErrorMap);

// ********************************
// * Basic/primitive schemas
// ********************************

const APIIdString = string().min(32, errorMessages.APIIdMin).max(32, errorMessages.APIIdMax);

const nullishNumber = number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
    .nonnegative(errorMessages.numberPositive)
    .nullish();

const nullishDecimal = number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
    .multipleOf(0.01, errorMessages.maxTwoDecimalPlaces)
    .nonnegative(errorMessages.numberPositive)
    .nullish();

const nullishPositiveNumber = number({
    invalid_type_error: errorMessages.numberType,
    required_error: errorMessages.required,
})
    .positive(errorMessages.numberPositive)
    .nullish();

const writableRequiredNumber = number({
    invalid_type_error: errorMessages.required,
    required_error: errorMessages.required,
})
    .nonnegative(errorMessages.numberPositive)
    .optional(); // allow undefined but no null

export const APIDateSchema = string({required_error: errorMessages.required}).regex(
    /^\d{4}-\d{2}-\d{2}$/,
    errorMessages.dateFormat
);

export const CodeSchema = object({
    id: APIIdString,
    value: string(),
    description: string().nullable(),
});

export const PostalCodeSchema = object({
    value: string(),
    city: string(),
    cost_area: z.enum(CostAreas),
});

export const AddressSchema = object({
    street_address: string({required_error: errorMessages.required}).min(2, errorMessages.stringLength),
    postal_code: z
        .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .refine((val) => val.toString().match(/^\d{5}$/), errorMessages.postalCodeFormat)
        .or(string().length(5)),
    city: string().min(2, errorMessages.stringLength).optional(),
});

const ImprovementSchema = object({
    name: string(),
    value: number(),
    completion_date: string(),
});
const MarketPriceIndexImprovementSchema = ImprovementSchema.and(
    object({
        no_deductions: boolean(),
    })
);
const ApartmentConstructionPriceIndexImprovementSchema = ImprovementSchema.and(
    object({
        depreciation_percentage: z.enum(["0.0", "2.5", "10.0"]),
    })
);

export const HousingCompanyImprovementsFormSchema = z.object({
    market_price_index: MarketPriceIndexImprovementSchema.array(),
    construction_price_index: ImprovementSchema.array(),
});
export type IHousingCompanyImprovementsForm = z.infer<typeof HousingCompanyImprovementsFormSchema>;

export const ApartmentImprovementsFormSchema = z.object({
    market_price_index: MarketPriceIndexImprovementSchema.array(),
    construction_price_index: ApartmentConstructionPriceIndexImprovementSchema.array(),
});
export type IApartmentImprovementsForm = z.infer<typeof ApartmentImprovementsFormSchema>;

export const UserInfoSchema = object({
    first_name: string(),
    last_name: string(),
    email: string(),
});

// ********************************
// * Housing company schemas
// ********************************

const HousingCompanyAreaSchema = object({name: string(), cost_area: number()});

const HousingCompanyHitasTypeSchema = z.enum(housingCompanyHitasTypes);
const HousingCompanyRegulationStatusSchema = z.enum(housingCompanyRegulationStatus);

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

const BuildingSchema = object({
    id: APIIdString,
    address: AddressSchema,
    building_identifier: string().nullable(),
    apartment_count: number(),
});

export const WritableBuildingSchema = object({
    id: APIIdString.optional(),
    address: object({street_address: string()}),
    building_identifier: string().nullable(),
    real_estate_id: APIIdString.nullable(),
});

const RealEstateSchema = object({
    id: APIIdString,
    property_identifier: string(),
    address: AddressSchema,
    buildings: BuildingSchema.array(),
});

export const WritableRealEstateSchema = object({
    id: APIIdString.optional(),
    property_identifier: string(),
});

export const PropertyManagerSchema = object({
    id: APIIdString.optional(),
    name: string().nonempty(errorMessages.required).min(2, errorMessages.stringLength),
    email: string().email(errorMessages.emailInvalid).or(z.literal("")),
});

export const DeveloperSchema = object({
    id: APIIdString.optional(),
    value: string().nonempty(errorMessages.required).min(2, errorMessages.stringLength),
    description: string()
        .nonempty(errorMessages.required)
        .min(2, errorMessages.stringLength)
        .max(256, errorMessages.stringMaxIs + "256")
        .nullable(),
});

const HousingCompanyDetailsSchema = object({
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
    acquisition_price: number(),
    primary_loan: number().optional(),
    sales_price_catalogue_confirmation_date: string().nullable(),
    notes: string().nullable(),
    archive_id: number(),
    release_date: string().nullable(),
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
});

export const HousingCompanyWritableSchema = HousingCompanyDetailsSchema.pick({
    name: true,
    business_id: true,
    hitas_type: true,
    exclude_from_statistics: true,
    regulation_status: true,
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

const HousingCompanyStateSchema = object({
    status: string(),
    housing_company_count: number(),
    apartment_count: number(),
});

// ********************************
// * Apartment Schemas
// ********************************

const ApartmentAddressSchema = object({
    street_address: string(),
    postal_code: string().optional(),
    city: string().optional(), // Read only
    apartment_number: writableRequiredNumber,
    floor: nullishNumber,
    stair: string().min(1, "Pakollinen kenttä!"),
});

const ApartmentLinkedModelSchema = object({id: string(), link: string()});

const ApartmentLinkedModelsSchema = object({
    housing_company: ApartmentLinkedModelSchema.merge(
        object({display_name: string(), regulation_status: HousingCompanyRegulationStatusSchema})
    ),
    real_estate: ApartmentLinkedModelSchema,
    building: ApartmentLinkedModelSchema.merge(object({street_address: string()})),
    apartment: ApartmentLinkedModelSchema,
});

export const OwnerSchema = object({
    id: APIIdString,
    name: string({required_error: errorMessages.required})
        .min(2, errorMessages.stringLength)
        .max(256, errorMessages.stringMaxIs + "256"),
    identifier: string({required_error: errorMessages.required})
        .min(1, errorMessages.stringLength)
        .max(11, errorMessages.stringMaxIs + "11"),
    email: string().email(errorMessages.emailInvalid).optional().or(z.literal("")),
    non_disclosure: boolean().optional(),
});

const ownershipSchema = object({
    owner: OwnerSchema,
    percentage: z
        .number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .positive(errorMessages.numberPositive)
        .max(100, errorMessages.numberMax),
    key: z.any(),
    starting_date: string().optional(),
});

export const ownershipsSchema = ownershipSchema.array();

// Condition of Sale
const CreateConditionOfSaleSchema = object({
    household: string().array(), // List of owner IDs
});

const ApartmentConditionOfSaleSchema = object({
    id: string(),
    owner: OwnerSchema.omit({id: true}).and(object({id: string()})),
    apartment: object({
        id: string(),
        address: ApartmentAddressSchema,
        housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
    }),
    grace_period: z.enum(["not_given", "three_months", "six_months"]),
    fulfilled: string().nullable(),
    sell_by_date: string().nullable(), // Read only
});

const ConditionOfSaleSchema = object({
    id: string().optional(),
    new_ownership: ownershipSchema.and(
        object({
            apartment: object({
                id: string(),
                address: ApartmentAddressSchema,
                housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
            }),
        })
    ),
    old_ownership: ownershipSchema.and(
        object({
            apartment: object({
                id: string(),
                address: ApartmentAddressSchema,
                housing_company: ApartmentLinkedModelSchema.and(object({display_name: string()})),
            }),
        })
    ),
    grace_period: z.enum(["not_given", "three_months", "six_months"]),
    fulfilled: string().nullable().optional(),
});
const ApartmentUnconfirmedMaximumPriceSchema = object({maximum: boolean(), value: number()});

const ApartmentUnconfirmedMaximumPriceIndicesSchema = object({
    construction_price_index: ApartmentUnconfirmedMaximumPriceSchema,
    market_price_index: ApartmentUnconfirmedMaximumPriceSchema,
    surface_area_price_ceiling: ApartmentUnconfirmedMaximumPriceSchema,
});

const ApartmentConfirmedMaximumPriceSchema = object({
    id: string().optional(),
    calculation_date: string(),
    confirmed_at: string(),
    created_at: string(),
    maximum_price: number(),
    valid: object({is_valid: boolean(), valid_until: string()}),
});

export const ApartmentPricesSchema = object({
    first_sale_purchase_price: number().nullable(), // Read only
    first_sale_share_of_housing_company_loans: number().nullable(), // Read only
    first_sale_acquisition_price: number().optional(), // Read only. (purchase_price + share_of_housing_company_loans)
    first_purchase_date: string().nullable(), // Read only
    current_sale_id: string().nullable(), // Read only
    latest_sale_purchase_price: number().nullable(), // Read only
    latest_purchase_date: string().nullable(), // Read only
    catalog_purchase_price: number().nullable(), // Read only
    catalog_share_of_housing_company_loans: number().nullable(), // Read only
    catalog_acquisition_price: number().nullable(), // Read only. (purchase_price + share_of_hosing_company_loans)
    construction: object({
        loans: nullishDecimal,
        additional_work: nullishDecimal,
        interest: object({
            rate_6: nullishDecimal,
            rate_14: nullishDecimal,
        }).optional(),
        debt_free_purchase_price: nullishDecimal,
    }),
    maximum_prices: object({
        // Read only
        confirmed: ApartmentConfirmedMaximumPriceSchema.nullable(),
        unconfirmed: object({
            onwards_2011: ApartmentUnconfirmedMaximumPriceIndicesSchema,
            pre_2011: ApartmentUnconfirmedMaximumPriceIndicesSchema,
        }),
    }),
});

const ApartmentWritablePricesSchema = ApartmentPricesSchema.omit({
    first_sale_purchase_price: true,
    first_sale_share_of_housing_company_loans: true,
    first_sale_acquisition_price: true,
    first_purchase_date: true,
    current_sale_id: true,
    latest_sale_purchase_price: true,
    latest_purchase_date: true,
    maximum_prices: true,
    catalog_purchase_price: true,
    catalog_share_of_housing_company_loans: true,
    catalog_acquisition_price: true,
});

export const ApartmentSharesSchema = object({
    start: nullishPositiveNumber,
    end: nullishPositiveNumber,
    total: number(),
});

export const ApartmentSchema = object({
    id: string().nullable(),
    is_sold: boolean(),
    type: string(),
    surface_area: number(),
    rooms: number().nullable(),
    address: ApartmentAddressSchema,
    completion_date: string().nullable(),
    housing_company: string(),
    ownerships: ownershipsSchema,
    links: ApartmentLinkedModelsSchema,
    has_conditions_of_sale: boolean(),
    has_grace_period: boolean(),
    sell_by_date: string().nullable(),
});

export const ApartmentDetailsSchema = object({
    id: APIIdString,
    is_sold: boolean(),
    type: CodeSchema,
    surface_area: number(),
    rooms: number().nullable(),
    shares: ApartmentSharesSchema,
    address: ApartmentAddressSchema,
    prices: ApartmentPricesSchema,
    completion_date: string().nullable(),
    ownerships: ownershipsSchema,
    notes: string(),
    improvements: object({
        market_price_index: MarketPriceIndexImprovementSchema.array(),
        construction_price_index: ApartmentConstructionPriceIndexImprovementSchema.array(),
    }),
    links: ApartmentLinkedModelsSchema,
    conditions_of_sale: ApartmentConditionOfSaleSchema.array(),
    sell_by_date: string().nullable(),
});

export const ApartmentWritableSchema = object({
    id: APIIdString.optional(),
    type: object({id: string()}).nullable(),
    surface_area: nullishDecimal,
    rooms: nullishNumber,
    shares: ApartmentSharesSchema.omit({total: true}),
    address: ApartmentAddressSchema,
    prices: ApartmentWritablePricesSchema,
    completion_date: string().nullish(),
    building: object({id: string()}),
    notes: string(),
    improvements: object({
        market_price_index: MarketPriceIndexImprovementSchema.array(),
        construction_price_index: ApartmentConstructionPriceIndexImprovementSchema.array(),
    }),
});

export const ApartmentWritableFormSchema = ApartmentWritableSchema.omit({
    building: true,
    address: true,
}).and(
    object({
        building: object({label: string(), value: string()}),
        address: ApartmentAddressSchema.omit({street_address: true, city: true}),
    })
);

// Writable list of ownerships
export const OwnershipsListSchema = object({
    owner: object({id: APIIdString.optional().or(z.literal(""))}),
    percentage: number({invalid_type_error: errorMessages.numberType, required_error: errorMessages.required})
        .multipleOf(0.01, errorMessages.maxTwoDecimalPlaces)
        .positive(errorMessages.numberPositive),
})
    .array()
    .superRefine((elements, ctx) => {
        // Can't have an empty ownerships list
        if (!elements.length) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: errorMessages.noOwnerships,
            });
            return;
        }

        // Check for duplicates
        const ownerIds = elements.filter((e) => e.owner.id).map((e) => e.owner.id);
        if (ownerIds.length !== new Set(ownerIds).size) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: errorMessages.ownershipDuplicate,
            });
        }

        // Prevent empty fields
        if (elements.filter((e) => !e.owner.id).length) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: `"Omistaja"-kenttä ei voi olla tyhjä`,
            });
            return;
        }
        if (elements.filter((e) => !e.percentage).length) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: "Prosenttikentän arvo on 0",
            });
            return;
        }

        // Sum of percentages must be 100
        const percentages = elements.map((e) => e.percentage);
        const percentagesSum = percentages.reduce((a, b) => a + b, 0);
        if (percentagesSum !== 0 && percentagesSum !== 100) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                message: errorMessages.ownershipPercent,
            });
        }
    });

// Writable Apartment Sale Form
export const ApartmentSaleFormSchema = object({
    key: string().optional(),
    notification_date: APIDateSchema,
    purchase_date: APIDateSchema,
    purchase_price: z
        .number({invalid_type_error: errorMessages.required, required_error: errorMessages.required})
        .nonnegative(errorMessages.priceMin)
        .max(999999, errorMessages.priceMax)
        .multipleOf(1, errorMessages.noDecimalPlaces)
        .nullish(),
    apartment_share_of_housing_company_loans: z
        .number({invalid_type_error: errorMessages.required, required_error: errorMessages.required})
        .nonnegative(errorMessages.loanShareMin)
        .multipleOf(1, errorMessages.noDecimalPlaces)
        .nullish(),
    exclude_from_statistics: boolean(),
    ownerships: OwnershipsListSchema.optional(),
});

// Apartment Sale Form that can be submitted.
// Other validations still need to be done, but those are out of scope for this schema.

export const ApartmentSaleSchema = ApartmentSaleFormSchema.omit({
    purchase_price: true,
    apartment_share_of_housing_company_loans: true,
    ownerships: true,
}).and(
    object({
        id: string().optional(),
        purchase_price: z
            .number({invalid_type_error: errorMessages.required, required_error: errorMessages.required})
            .nonnegative(errorMessages.priceMin)
            .max(999999, errorMessages.priceMax),
        apartment_share_of_housing_company_loans: z
            .number({invalid_type_error: errorMessages.required, required_error: errorMessages.required})
            .nonnegative(errorMessages.priceMin),
        ownerships: OwnershipsListSchema,
    })
);

const ApartmentSaleCreatedSchema = object({
    id: string(),
    ownerships: object({owner: object({id: APIIdString}), percentage: number()}).array(),
    notification_date: string(),
    purchase_date: string(),
    purchase_price: number(),
    apartment_share_of_housing_company_loans: number(),
    exclude_from_statistics: boolean(),
    conditions_of_sale_created: boolean(),
});

// ********************************
// * Maximum price schemas
// ********************************

// Maximum Price Fields

const IndexCalculationSchema = object({
    maximum_price: number(),
    valid_until: string(),
    maximum: boolean(),
    calculation_variables: z.unknown(),
});

// Used in both MPI and RKI before and after 2011
const CommonCalculationVarsSchema = object({
    debt_free_price: number(),
    debt_free_price_m2: number(),
    apartment_share_of_housing_company_loans: number(),
    apartment_share_of_housing_company_loans_date: string(),
    completion_date: string(),
    completion_date_index: number(),
    calculation_date: string(),
    calculation_date_index: number(),
});

const CalculationVars2011OnwardsSchema = object({
    first_sale_acquisition_price: number(),
    additional_work_during_construction: number(),
    basic_price: number(),
    index_adjustment: number(),
    housing_company_improvements: object({
        items: object({
            name: string(),
            value: number(),
            value_added: number(),
            completion_date: string(),
            value_for_apartment: number(),
            value_for_housing_company: number(),
        }).array(),
        summary: object({
            value: number(),
            value_added: number(),
            excess: object({
                total: number(),
                surface_area: number(),
                value_per_square_meter: number(),
            }),
            value_for_housing_company: number(),
            value_for_apartment: number(),
        }),
    }),
});

const IndexCalculation2011OnwardsSchema = IndexCalculationSchema.and(
    object({
        calculation_variables: CommonCalculationVarsSchema.and(CalculationVars2011OnwardsSchema),
    })
);

const IndexCalculationMarketPriceIndexBefore2011Schema = IndexCalculationSchema.and(
    object({
        calculation_variables: CommonCalculationVarsSchema.and(
            object({
                first_sale_acquisition_price: number(),
                interest_during_construction: number(),
                interest_during_construction_percentage: number(),
                additional_work_during_construction: number(),
                basic_price: number(),
                index_adjustment: number(),
                apartment_improvements: object({
                    items: object({
                        name: string(),
                        value: number(),
                        depreciation: object({
                            time: object({
                                years: number(),
                                months: number(),
                            }),
                            amount: number(),
                        }),
                        accepted_value: number(),
                        completion_date: string(),
                        value_without_excess: number(),
                    }).array(),
                    summary: object({
                        value: number(),
                        excess: object({
                            total: number(),
                            surface_area: number(),
                            value_per_square_meter: number(),
                        }),
                        depreciation: number(),
                        accepted_value: number(),
                        value_without_excess: number(),
                    }),
                }),
                housing_company_improvements: object({
                    items: object({
                        name: string(),
                        value: number(),
                        depreciation: object({
                            time: object({
                                years: number(),
                                months: number(),
                            }),
                            amount: number(),
                        }),
                        accepted_value: number(),
                        completion_date: string(),
                        value_without_excess: number(),
                        accepted_value_for_housing_company: number(),
                    }).array(),
                    summary: object({
                        value: number(),
                        excess: object({
                            total: number(),
                            surface_area: number(),
                            value_per_square_meter: number(),
                        }),
                        depreciation: number(),
                        accepted_value: number(),
                        value_without_excess: number(),
                        accepted_value_for_housing_company: number(),
                    }),
                }),
            })
        ),
    })
);

const IndexCalculationConstructionPriceIndexBefore2011Schema = IndexCalculationSchema.and(
    object({
        calculation_variables: CommonCalculationVarsSchema.and(
            object({
                interest_during_construction: number(),
                interest_during_construction_percentage: number(),
                housing_company_acquisition_price: number(),
                housing_company_assets: number(),
                apartment_share_of_housing_company_assets: number(),
                additional_work_during_construction: number(),
                index_adjusted_additional_work_during_construction: number(),
                apartment_improvements: object({
                    items: object({
                        name: string(),
                        value: number(),
                        depreciation: object({
                            time: object({
                                years: number(),
                                months: number(),
                            }),
                            amount: number(),
                            percentage: number(),
                        }),
                        index_adjusted: number(),
                        completion_date: string(),
                        value_for_apartment: number(),
                        completion_date_index: number(),
                        calculation_date_index: number(),
                    }).array(),
                    summary: object({
                        value: number(),
                        depreciation: number(),
                        index_adjusted: number(),
                        value_for_apartment: number(),
                    }),
                }),
                housing_company_improvements: object({
                    items: object({
                        name: string(),
                        value: number(),
                        value_for_apartment: number(),
                    }).array(),
                    summary: object({
                        value: number(),
                        value_for_apartment: number(),
                    }),
                }),
            })
        ),
    })
);

const SurfaceAreaPriceCeilingCalculationSchema = IndexCalculationSchema.and(
    object({
        calculation_variables: object({
            calculation_date: string(),
            calculation_date_value: number(),
            debt_free_price: number(),
            surface_area: number(),
            apartment_share_of_housing_company_loans: number(),
            apartment_share_of_housing_company_loans_date: string(),
        }),
    })
);

// Maximum Price Schemas

export const ApartmentMaximumPrice2011OnwardsSchema = object({
    new_hitas: literal(true),
    calculations: object({
        construction_price_index: IndexCalculation2011OnwardsSchema,
        market_price_index: IndexCalculation2011OnwardsSchema,
        surface_area_price_ceiling: SurfaceAreaPriceCeilingCalculationSchema,
    }),
});

export const ApartmentMaximumPricePre2011Schema = object({
    new_hitas: literal(false),
    calculations: object({
        construction_price_index: IndexCalculationConstructionPriceIndexBefore2011Schema,
        market_price_index: IndexCalculationMarketPriceIndexBefore2011Schema,
        surface_area_price_ceiling: SurfaceAreaPriceCeilingCalculationSchema,
    }),
});

const Split2011Schema = ApartmentMaximumPrice2011OnwardsSchema.or(ApartmentMaximumPrice2011OnwardsSchema);

export const ApartmentMaximumPriceSchema = object({
    id: string(),
    index: z.enum(indexNames),
    maximum_price: number(),
    maximum_price_per_square: number(),
    created_at: string(),
    confirmed_at: string().nullable(),
    calculation_date: string(),
    valid_until: string(),
    additional_info: string(),
    apartment: object({
        address: ApartmentAddressSchema,
        type: string(),
        ownerships: object({
            name: string(),
            percentage: number(),
        }).array(),
        rooms: number().nullable(),
        shares: ApartmentSharesSchema,
        surface_area: number(),
    }),
    housing_company: object({
        archive_id: number(),
        official_name: string(),
        property_manager: object({
            name: string(),
            street_address: string(),
        }),
    }),
}).and(Split2011Schema);

export const ApartmentMaximumPriceWritableSchema = object({
    calculation_date: string().nullable(),
    apartment_share_of_housing_company_loans: number().nullable(),
    apartment_share_of_housing_company_loans_date: string().nullable(),
    additional_info: string(),
});

const IndexSchema = object({indexType: string(), month: string(), value: number().nullable()});

export const IndexResponseSchema = object({indexType: string(), value: number(), valid_until: string()});

const ThirtyYearRegulationCompanySchema = object({
    id: string(),
    display_name: string(),
    price: number(),
    old_ruleset: boolean(),
    property_manager: object({
        email: string(),
        id: APIIdString,
        name: string(),
    }),
});

const ThirtyYearRegulationResponseSchema = object({
    automatically_released: ThirtyYearRegulationCompanySchema.array(),
    released_from_regulation: ThirtyYearRegulationCompanySchema.array(),
    stays_regulated: ThirtyYearRegulationCompanySchema.array(),
    skipped: ThirtyYearRegulationCompanySchema.array(),
    obfuscated_owners: OwnerSchema.array(),
});

const ThirtyYearAvailablePostalCodeSchema = object({
    postal_code: string(),
    price_by_area: number(),
    cost_area: number(),
});

const ThirtyYearAvailablePostalCodesResponseSchema = ThirtyYearAvailablePostalCodeSchema.array();

const QuarterSchema = string().regex(/\d{4}Q\d/);
const ExternalSalesQuarterSchema = object({
    quarter: QuarterSchema,
    areas: object({
        postal_code: string().regex(/\d{3}/),
        sale_count: number(),
        price: number(),
    }).array(),
});
const ExternalSalesDataResponseSchema = object({
    calculation_quarter: QuarterSchema,
    quarter_1: ExternalSalesQuarterSchema,
    quarter_2: ExternalSalesQuarterSchema,
    quarter_3: ExternalSalesQuarterSchema,
    quarter_4: ExternalSalesQuarterSchema,
});

// ********************************
// * Request / Response schemas
// ********************************

// General

const PageInfoSchema = object({
    size: number(),
    total_items: number(),
    current_page: number(),
    total_pages: number(),
    links: object({
        next: string().nullable(),
        previous: string().nullable(),
    }),
});

const ErrorResponseSchema = object({
    error: string(),
    status: number(),
    reason: string(),
    message: string(),
    fields: object({
        field: string(),
        message: string(),
    })
        .array()
        .optional(),
    data: object({
        status: number(),
        data: object({
            error: string(),
            message: string(),
            reason: string(),
            status: number(),
        }),
    }).optional(),
});

// List responses

export const HousingCompanyListResponseSchema = object({
    page: PageInfoSchema,
    contents: HousingCompanySchema.array(),
});

export const ApartmentListResponseSchema = object({
    page: PageInfoSchema,
    contents: ApartmentSchema.array(),
});

export const CodeResponseSchema = object({
    page: PageInfoSchema,
    contents: CodeSchema.array(),
});

export const PostalCodeResponseSchema = object({
    page: PageInfoSchema,
    contents: PostalCodeSchema.array(),
});

export const IndexListResponseSchema = object({
    page: PageInfoSchema,
    contents: IndexSchema.array(),
});

export const OwnersResponseSchema = object({
    page: PageInfoSchema,
    contents: OwnerSchema.array(),
});

const SalesCatalogApartmentSchema = object({
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

export const PropertyManagersResponseSchema = object({
    page: PageInfoSchema,
    contents: array(PropertyManagerSchema.extend({id: string()})),
});

// Query Parameters

export const HousingCompanyApartmentQuerySchema = object({
    housingCompanyId: string(),
    params: object({
        page: number(),
    }),
});

export const ApartmentQuerySchema = object({
    housingCompanyId: string(),
    apartmentId: string(),
});

export const IndexListQuerySchema = object({
    indexType: string(),
    params: object({
        page: number(),
        limit: number(),
        year: string(),
    }),
});

const IndexQuerySchema = object({
    indexType: string(),
    month: string(),
});

const ThirtyYearRegulationQuerySchema = object({
    calculationDate: string(),
    replacementPostalCodes: object({
        postalCode: string(),
        replacements: string().array(),
    })
        .array()
        .optional(),
});

export const FilterOwnersQuerySchema = object({
    name: string().optional(),
    identifier: string().optional(),
    email: string().optional(),
    limit: number().int().optional(),
    page: number().int().optional(),
});

export const FilterPropertyManagersQuerySchema = object({
    name: string().optional(),
    email: string().optional(),
    limit: number().int().optional(),
    page: number().int().optional(),
});

export const FilterDevelopersQuerySchema = object({
    value: string().optional(),
    limit: number().int().optional(),
    page: number().int().optional(),
});

// ********************************
// * Exports
// ********************************

// Types (i.e. models)
export type IAddress = z.infer<typeof AddressSchema>;
export type IHousingCompany = z.infer<typeof HousingCompanySchema>;
export type IHousingCompanyDetails = z.infer<typeof HousingCompanyDetailsSchema>;
export type IHousingCompanyWritable = z.infer<typeof HousingCompanyWritableSchema>;
export type IHousingCompanyState = z.infer<typeof HousingCompanyStateSchema>;
export type IRealEstate = z.infer<typeof RealEstateSchema>;
export type IBuilding = z.infer<typeof BuildingSchema>;
export type IBuildingWritable = z.infer<typeof WritableBuildingSchema>;
export type IApartmentAddress = z.infer<typeof ApartmentAddressSchema>;
export type IApartmentUnconfirmedMaximumPrice = z.infer<typeof ApartmentUnconfirmedMaximumPriceSchema>;
export type IApartmentUnconfirmedMaximumPriceIndices = z.infer<typeof ApartmentUnconfirmedMaximumPriceIndicesSchema>;
export type IApartmentConfirmedMaximumPrice = z.infer<typeof ApartmentConfirmedMaximumPriceSchema>;
export type IApartmentConstructionPriceIndexImprovement = z.infer<
    typeof ApartmentConstructionPriceIndexImprovementSchema
>;
export type IApartment = z.infer<typeof ApartmentSchema>;
export type IApartmentDetails = z.infer<typeof ApartmentDetailsSchema>;
export type IApartmentWritable = z.infer<typeof ApartmentWritableSchema>;
export type IApartmentWritableForm = z.infer<typeof ApartmentWritableFormSchema>;
export type IApartmentSale = z.infer<typeof ApartmentSaleSchema>;
export type IApartmentSaleForm = z.infer<typeof ApartmentSaleFormSchema>;
export type IApartmentSaleCreated = z.infer<typeof ApartmentSaleCreatedSchema>;
export type IIndexCalculation2011Onwards = z.infer<typeof IndexCalculation2011OnwardsSchema>;
export type IIndexCalculationMarketPriceIndexBefore2011 = z.infer<
    typeof IndexCalculationMarketPriceIndexBefore2011Schema
>;
export type IIndexCalculationConstructionPriceIndexBefore2011 = z.infer<
    typeof IndexCalculationConstructionPriceIndexBefore2011Schema
>;
export type SurfaceAreaPriceCeilingCalculation = z.infer<typeof SurfaceAreaPriceCeilingCalculationSchema>;
export type IApartmentMaximumPriceCalculationDetails = z.infer<typeof ApartmentMaximumPriceSchema>;
export type IApartmentMaximumPriceWritable = z.infer<typeof ApartmentMaximumPriceWritableSchema>;
export type IIndex = z.infer<typeof IndexSchema>;
export type ICode = z.infer<typeof CodeSchema>;
export type IPostalCode = z.infer<typeof PostalCodeSchema>;
export type IPropertyManager = z.infer<typeof PropertyManagerSchema>;
export type IOwner = z.infer<typeof OwnerSchema>;
export type IDeveloper = z.infer<typeof DeveloperSchema>;
export type IOwnership = z.infer<typeof ownershipSchema>;

// Query/list responses & paging
export type PageInfo = z.infer<typeof PageInfoSchema>;
export type IUserInfoResponse = z.infer<typeof UserInfoSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
export type IHousingCompanyListResponse = z.infer<typeof HousingCompanyListResponseSchema>;
export type IApartmentListResponse = z.infer<typeof ApartmentListResponseSchema>;
export type ICodeResponse = z.infer<typeof CodeResponseSchema>;
export type IOwnersResponse = z.infer<typeof OwnersResponseSchema>;
export type IPropertyManagersResponse = z.infer<typeof PropertyManagersResponseSchema>;
export type IPostalCodeResponse = z.infer<typeof PostalCodeResponseSchema>;
export type ISalesCatalogApartment = z.infer<typeof SalesCatalogApartmentSchema>;
export type IHousingCompanyApartmentQuery = z.infer<typeof HousingCompanyApartmentQuerySchema>;
export type IApartmentQuery = z.infer<typeof ApartmentQuerySchema>;
export type IIndexListQuery = z.infer<typeof IndexListQuerySchema>;
export type IIndexListResponse = z.infer<typeof IndexListResponseSchema>;
export type IIndexQuery = z.infer<typeof IndexQuerySchema>;
export type IIndexResponse = z.infer<typeof IndexResponseSchema>;
export type IFilterOwnersQuery = z.infer<typeof FilterOwnersQuerySchema>;
export type IFilterPropertyManagersQuery = z.infer<typeof FilterPropertyManagersQuerySchema>;
export type IFilterDevelopersQuery = z.infer<typeof FilterDevelopersQuerySchema>;

export type IExternalSalesDataResponse = z.infer<typeof ExternalSalesDataResponseSchema>;
export type IThirtyYearRegulationResponse = z.infer<typeof ThirtyYearRegulationResponseSchema>;
export type IThirtyYearAvailablePostalCodesResponse = z.infer<typeof ThirtyYearAvailablePostalCodesResponseSchema>;
export type IThirtyYearRegulationQuery = z.infer<typeof ThirtyYearRegulationQuerySchema>;

export type IApartmentConditionOfSale = z.infer<typeof ApartmentConditionOfSaleSchema>;
export type IConditionOfSale = z.infer<typeof ConditionOfSaleSchema>;
export type ICreateConditionOfSale = z.infer<typeof CreateConditionOfSaleSchema>;
