export const housingCompanyHitasTypes = [
    "non_hitas",
    "hitas_1",
    "hitas_2",
    "hitas_1_no_interest",
    "hitas_2_no_interest",
    "new_hitas_1",
    "new_hitas_2",
    "rr_new_hitas",
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

export const CostAreas = ["1", "2", "3", "4"] as const;
