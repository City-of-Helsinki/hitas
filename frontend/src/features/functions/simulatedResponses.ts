const comparisonResponses = {
    result_noProblems: {
        automatically_released: [
            {
                id: "dccd2cbc98264f28b097da8209441bbf",
                display_name: "Helsingin Rumpupolun palvelutalo",
                address: {
                    street_address: "Fakestreet 123",
                    postal_code: "00100",
                    city: "Helsinki",
                },
                price: 0.0,
                old_ruleset: false,
                completion_date: "2014-06-02",
                property_manager: {
                    id: "dc1072975bab4ba69f64814f021c6785",
                    name: "Ismo Isännöitsijät Oy",
                    email: "ismo@example.com",
                    address: {
                        street_address: "Torikatu 16 B 4",
                        postal_code: "90100",
                        city: "Oulu",
                    },
                },
                letter_fetched: true,
            },
        ],
        released_from_regulation: [
            {
                id: "7938b3fd2b774139b0b7f410758e09c6",
                display_name: "Karjalainen",
                address: {
                    street_address: "Yrttimaanpolku 020",
                    postal_code: "00530",
                    city: "Helsinki",
                },
                price: 12000.0,
                old_ruleset: true,
                completion_date: "2014-06-02",
                property_manager: {
                    id: "dc1072975bab4ba69f64814f021c6785",
                    name: "Ismo Isännöitsijät Oy",
                    email: "ismo@example.com",
                    address: {
                        street_address: "Torikatu 16 B 4",
                        postal_code: "90100",
                        city: "Oulu",
                    },
                },
                letter_fetched: false,
            },
        ],
        stays_regulated: [
            {
                id: "01c9168e637b4ce0947802e9b417d15a",
                display_name: "Jokela",
                address: {
                    street_address: "Biologinkuja 3",
                    postal_code: "00200",
                    city: "Helsinki",
                },
                price: 1337.0,
                old_ruleset: true,
                completion_date: "2014-06-02",
                property_manager: {
                    id: "dc1072975bab4ba69f64814f021c6785",
                    name: "Ismo Isännöitsijät Oy",
                    email: "ismo@example.com",
                    address: {
                        street_address: "Torikatu 16 B 4",
                        postal_code: "90100",
                        city: "Oulu",
                    },
                },
                letter_fetched: false,
            },
        ],
        skipped: [],
        obfuscated_owners: [
            {
                name: "Olavi Toivonen",
                identifier: "7107925-4",
                email: "zoinonen@example.com",
            },
            {
                name: "Eemeli Rinne",
                identifier: "7107925-4",
                email: "teemumakinen@example.com",
            },
        ],
    },
    result_skippedCompany: {
        automatically_released: [],
        obfuscated_owners: [],
        released_from_regulation: [],
        skipped: [
            {
                address: {
                    city: "Helsinki",
                    postal_code: "00100",
                    street_address: "Disankuja 14",
                },
                completion_date: "1993-02-01",
                display_name: "Lassila",
                id: "d766a637751d4c58913ccaabf5f10b6c",
                old_ruleset: true,
                price: 12000.0,
                property_manager: {
                    address: {
                        city: "Liperi",
                        postal_code: "95024",
                        street_address: "Edelfeltinkatu 7",
                    },
                    email: "kari06@example.net",
                    id: "216f86ca32ff49cea26fe8e2d9447e8f",
                    name: "Maria Kyll\u00f6nen-Jokinen",
                },
            },
            {
                address: {
                    city: "Helsinki",
                    postal_code: "00120",
                    street_address: "Disankuja 14",
                },
                completion_date: "1993-02-01",
                display_name: "Virtanen",
                id: "2980ec0868874297820c4150f9146620",
                old_ruleset: true,
                price: 12000.0,
                property_manager: {
                    address: {
                        city: "Liperi",
                        postal_code: "95024",
                        street_address: "Edelfeltinkatu 7",
                    },
                    email: "kari06@example.net",
                    id: "216f86ca32ff49cea26fe8e2d9447e8f",
                    name: "Maria Kyll\u00f6nen-Jokinen",
                },
            },
            {
                address: {
                    city: "Helsinki",
                    postal_code: "00100",
                    street_address: "Disankuja 14",
                },
                completion_date: "1993-02-01",
                display_name: "Test Housing company 003",
                id: "e3c34b7f47c74ef796bd51e8fbbe0929",
                old_ruleset: true,
                price: 12000.0,
                property_manager: {
                    address: {
                        city: "Liperi",
                        postal_code: "95024",
                        street_address: "Edelfeltinkatu 7",
                    },
                    email: "kari06@example.net",
                    id: "216f86ca32ff49cea26fe8e2d9447e8f",
                    name: "Maria Kyll\u00f6nen-Jokinen",
                },
            },
            {
                address: {
                    city: "Helsinki",
                    postal_code: "00100",
                    street_address: "Disankuja 14",
                },
                completion_date: "1993-02-01",
                display_name: "Test Housing company 004",
                id: "e3c34b7f47c74ef796bd51e8fbbe0929",
                old_ruleset: true,
                price: 12000.0,
                property_manager: {
                    address: {
                        city: "Liperi",
                        postal_code: "95024",
                        street_address: "Edelfeltinkatu 7",
                    },
                    email: "kari06@example.net",
                    id: "216f86ca32ff49cea26fe8e2d9447e8f",
                    name: "Maria Kyll\u00f6nen-Jokinen",
                },
            },
            {
                address: {
                    city: "Helsinki",
                    postal_code: "00100",
                    street_address: "Disankuja 14",
                },
                completion_date: "1993-02-01",
                display_name: "Test Housing company 005",
                id: "e3c34b7f47c74ef796bd51e8fbbe0929",
                old_ruleset: true,
                price: 12000.0,
                property_manager: {
                    address: {
                        city: "Liperi",
                        postal_code: "95024",
                        street_address: "Edelfeltinkatu 7",
                    },
                    email: "kari06@example.net",
                    id: "216f86ca32ff49cea26fe8e2d9447e8f",
                    name: "Maria Kyll\u00f6nen-Jokinen",
                },
            },
        ],
        stays_regulated: [],
    },
    result_noCompanies: {
        automatically_released: [],
        obfuscated_owners: [],
        released_from_regulation: [],
        skipped: [],
        stays_regulated: [],
    },
    error_missingIndex: {
        error: "missing_values",
        fields: [
            {
                field: "non_field_errors",
                message: "Pre 2011 market price indices missing for months: '1993-02', '2023-02'.",
            },
        ],
        message: "Missing required indices",
        reason: "Conflict",
        status: 409,
    },
    error_missingExcel: {
        error: "external_sales_data_not_found",
        message: "External sales data not found",
        reason: "Not Found",
        status: 404,
    },
    error_missingPriceCeiling: {
        error: "surface_area_price_ceiling_not_found",
        message: "Surface area price ceiling not found",
        reason: "Not Found",
        status: 404,
    },
    error_missingSurfaceArea: {
        error: "missing_values",
        fields: [
            {
                field: "non_field_errors",
                message:
                    "Average price per square meter could not be calculated for 'Test Housing company 000': Apartment 'Uurtajanpolku 5 t 75' does not have surface area set.",
            },
        ],
        message: "Missing apartment details",
        reason: "Conflict",
        status: 409,
    },
    error_zeroSurfaceArea: {
        error: "bad_request",
        fields: [
            {
                field: "non_field_errors",
                message:
                    "Average price per square meter zero or missing for these housing companies: 'Test Housing company 000'. Index adjustments cannot be made.",
            },
        ],
        message: "Bad request",
        reason: "Bad Request",
        status: 400,
    },
    error_alreadyCompared: {
        error: "unique",
        message: "Previous regulation exists. Cannot re-check regulation for this quarter.",
        reason: "Conflict",
        status: 409,
    },
};

const fileImportResponses = {
    success: {
        calculation_quarter: "2022Q4",
        quarter_1: {
            quarter: "2022Q1",
            areas: [
                {postal_code: "00180", sale_count: 77, price: 8304},
                {postal_code: "00220", sale_count: 19, price: 8255},
                {postal_code: "00280", sale_count: 19, price: 6747},
                {postal_code: "00300", sale_count: 17, price: 5577},
                {postal_code: "00310", sale_count: 8, price: 4222},
                {postal_code: "00540", sale_count: 18, price: 7684},
                {postal_code: "00570", sale_count: 34, price: 6527},
                {postal_code: "00580", sale_count: 29, price: 8156},
                {postal_code: "00650", sale_count: 21, price: 3810},
                {postal_code: "00680", sale_count: 12, price: 4072},
                {postal_code: "00690", sale_count: 10, price: 3608},
                {postal_code: "00870", sale_count: 20, price: 3556},
            ],
        },
        quarter_2: {
            quarter: "2022Q2",
            areas: [
                {postal_code: "00180", sale_count: 82, price: 8101},
                {postal_code: "00220", sale_count: 22, price: 7369},
                {postal_code: "00280", sale_count: 16, price: 6573},
                {postal_code: "00300", sale_count: 26, price: 5745},
                {postal_code: "00310", sale_count: 7, price: 4674},
                {postal_code: "00540", sale_count: 26, price: 8841},
                {postal_code: "00570", sale_count: 31, price: 6642},
                {postal_code: "00580", sale_count: 24, price: 8399},
                {postal_code: "00590", sale_count: 12, price: 5073},
                {postal_code: "00650", sale_count: 22, price: 4108},
                {postal_code: "00680", sale_count: 10, price: 3841},
                {postal_code: "00690", sale_count: 10, price: 3931},
                {postal_code: "00870", sale_count: 18, price: 3316},
            ],
        },
        quarter_3: {
            quarter: "2022Q3",
            areas: [
                {postal_code: "00180", sale_count: 62, price: 8504},
                {postal_code: "00220", sale_count: 22, price: 8842},
                {postal_code: "00280", sale_count: 16, price: 6341},
                {postal_code: "00300", sale_count: 15, price: 5807},
                {postal_code: "00540", sale_count: 13, price: 8941},
                {postal_code: "00570", sale_count: 25, price: 6589},
                {postal_code: "00580", sale_count: 21, price: 7808},
                {postal_code: "00650", sale_count: 18, price: 5129},
                {postal_code: "00690", sale_count: 6, price: 3827},
                {postal_code: "00850", sale_count: 11, price: 4566},
                {postal_code: "00870", sale_count: 19, price: 3521},
            ],
        },
        quarter_4: {
            quarter: "2022Q4",
            areas: [
                {postal_code: "00180", sale_count: 33, price: 7919},
                {postal_code: "00220", sale_count: 17, price: 8115},
                {postal_code: "00570", sale_count: 13, price: 6129},
                {postal_code: "00580", sale_count: 13, price: 7777},
            ],
        },
    },
    failure: {
        fileExists: {
            error: "unique",
            message: "External sales data already exists for '2023Q1'",
            reason: "Conflict",
            status: 409,
        },
        wrongQuarter: {
            error: "bad_request",
            fields: [
                {
                    field: "calculation_date",
                    message: "Given Excel is not for this Hitas quarter.",
                },
            ],
            message: "Bad request",
            reason: "Bad Request",
            status: 400,
        },
    },
};

const priceCeilings = {
    2023: {
        "02-01": 4621,
    },
    2022: {
        "02-01": 2201,
        "05-01": 2202,
        "08-01": 2203,
        "11-01": 2204,
    },
    2021: {
        "02-01": 2101,
        "05-01": 2102,
        "08-01": 2103,
        "11-01": 2104,
    },
    TEST: {
        "02-01": "TEST",
        "05-01": "TEST",
        "08-01": "TEST",
        "11-01": "TEST",
    },
};

export {comparisonResponses, fileImportResponses, priceCeilings};
