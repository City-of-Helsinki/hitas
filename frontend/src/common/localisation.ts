export const getHousingCompanyStateName = (state) => {
    switch (state) {
        case "not_ready":
            return "Ei valmis";
        case "lt_30_years":
            return "Alle 30-vuotta";
        case "gt_30_years_not_free":
            return "Yli 30-vuotta, ei vapautunut";
        case "gt_30_years_free":
            return "Yli 30-vuotta, vapautunut";
        case "gt_30_years_plot_department_notification":
            return "Yli 30-vuotta, vapautunut tonttiosaston ilmoitus";
        case "half_hitas":
            return "Puoli-hitas";
        case "ready_no_statistics":
            return "Valmis, ei tilastoihin";
        default:
            return "VIRHE";
    }
};

export function getIndexType(indexType: string) {
    switch (indexType) {
        case "market_price_index":
            return "markkinahintaindeksi";
        case "construction_price_index":
            return "rakennuskustannusindeksi";
        case "surface_area_price_ceiling":
            return "rajaneliöhintaindeksi";
        default:
            return "VIRHE";
    }
}

export const getApartmentStateLabel = (state) => {
    switch (state) {
        case "free":
            return "Vapaa";
        case "reserved":
            return "Varattu";
        case "sold":
            return "Myyty";
        default:
            return "VIRHE";
    }
};
