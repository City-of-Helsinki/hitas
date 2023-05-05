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

export const getHousingCompanyHitasTypeName = (state) => {
    switch (state) {
        case "non_hitas":
            return "Ei Hitas";
        case "hitas_1":
            return "Hitas I";
        case "hitas_2":
            return "Hitas II";
        case "hitas_1_no_interest":
            return "Hitas I, Ei korkoja";
        case "hitas_2_no_interest":
            return "Hitas II, Ei korkoja";
        case "new_hitas_1":
            return "Uusi Hitas I";
        case "new_hitas_2":
            return "Uusi Hitas II";
        case "half_hitas":
            return "Puolihitas";
        case "rental_hitas_1":
            return "Vuokratalo Hitas I";
        case "rental_hitas_2":
            return "Vuokratalo Hitas II";
        default:
            return "VIRHE";
    }
};

export const getHousingCompanyRegulationStatusName = (state) => {
    switch (state) {
        case "regulated":
            return "Ei vapautunut";
        case "released_by_hitas":
            return "Vapautunut 30v vertailussa";
        case "released_by_plot_department":
            return "Vapautunut tontit-yksikön päätöksellä";
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
