-- ripadb schema: tables, indexes, and materialized views
-- Run against the ripadb database after creating it.

-- ============================================================
-- Drop existing objects (idempotent reload)
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mv_agency_year_age CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_agency_year_gender CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_agency_year_race CASCADE;
DROP TABLE IF EXISTS agencies CASCADE;
DROP TABLE IF EXISTS stops CASCADE;
DROP TABLE IF EXISTS rae_labels CASCADE;
DROP TABLE IF EXISTS gender_labels CASCADE;
DROP TABLE IF EXISTS reason_labels CASCADE;
DROP TABLE IF EXISTS age_group_labels CASCADE;

-- ============================================================
-- Lookup tables
-- ============================================================
CREATE TABLE rae_labels (
    code SMALLINT PRIMARY KEY,
    label TEXT NOT NULL
);
INSERT INTO rae_labels (code, label) VALUES
    (1, 'Asian'),
    (2, 'Black/African American'),
    (3, 'Hispanic/Latino(a)'),
    (4, 'Middle Eastern/South Asian'),
    (5, 'Native American'),
    (6, 'Pacific Islander'),
    (7, 'White'),
    (8, 'Multiracial');

CREATE TABLE gender_labels (
    code SMALLINT PRIMARY KEY,
    label TEXT NOT NULL
);
INSERT INTO gender_labels (code, label) VALUES
    (1, 'Cisgender Man'),
    (2, 'Cisgender Woman'),
    (3, 'Transgender Man'),
    (4, 'Transgender Woman'),
    (5, 'Nonbinary Person'),
    (6, 'Multigender');

CREATE TABLE reason_labels (
    code SMALLINT PRIMARY KEY,
    label TEXT NOT NULL
);
INSERT INTO reason_labels (code, label) VALUES
    (1, 'Traffic violation'),
    (2, 'Reasonable suspicion'),
    (3, 'Known to be on parole/probation/PRCS/mandatory supervision'),
    (4, 'Knowledge of outstanding arrest warrant/wanted person'),
    (5, 'Investigation to determine whether student violated school policy'),
    (6, 'Consensual encounter resulting in a search'),
    (7, 'Possible conduct warranting discipline under Education Code'),
    (8, 'Determine whether to issue truancy-related document'),
    (9, 'Probable cause to arrest'),
    (10, 'Welfare & Institutions Code 5150');

CREATE TABLE age_group_labels (
    code SMALLINT PRIMARY KEY,
    label TEXT NOT NULL
);
INSERT INTO age_group_labels (code, label) VALUES
    (1, '1-9'),
    (2, '10-14'),
    (3, '15-17'),
    (4, '18-24'),
    (5, '25-34'),
    (6, '35-44'),
    (7, '45-54'),
    (8, '55-64'),
    (9, '65+');

-- ============================================================
-- Main stops table (all 235 columns, lowercased)
-- ============================================================
CREATE TABLE stops (
    id SERIAL PRIMARY KEY,

    -- Metadata
    data_year SMALLINT NOT NULL,
    county TEXT,
    quarter SMALLINT,
    source_file TEXT,

    -- Identifiers
    doj_record_id TEXT,
    person_number INTEGER,
    agency_ori TEXT,
    agency_name TEXT,
    non_reporting_agency TEXT,

    -- Stop context
    time_of_stop TEXT,
    date_of_stop TEXT,
    stop_duration INTEGER,
    loc_closest_city TEXT,

    -- School
    school_code TEXT,
    school_name TEXT,
    stop_student SMALLINT,
    k12_school_grounds SMALLINT,

    -- Race/ethnicity
    rae_full SMALLINT,
    rae_asian SMALLINT,
    rae_black_african_american SMALLINT,
    rae_hispanic_latinex SMALLINT,
    rae_middle_eastern_south_asian SMALLINT,
    rae_native_american SMALLINT,
    rae_pacific_islander SMALLINT,
    rae_white SMALLINT,
    rae_multiracial SMALLINT,

    -- Gender
    g_full SMALLINT,
    g_cisgender_man SMALLINT,
    g_cisgender_woman SMALLINT,
    g_transgender_man SMALLINT,
    g_transgender_woman SMALLINT,
    g_nonbinary_person SMALLINT,
    g_multigender SMALLINT,

    -- Sexual orientation
    sor_lgb SMALLINT,
    sor_straight SMALLINT,

    -- Age
    age INTEGER,
    age_group SMALLINT,
    age_group_orig SMALLINT,

    -- Other demographics
    limited_english_fluency SMALLINT,
    pd_full SMALLINT,
    pd_deafness_hearing SMALLINT,
    pd_speech_impair SMALLINT,
    pd_blind SMALLINT,
    pd_mental_health SMALLINT,
    pd_devel_disab SMALLINT,
    pd_hyperactivity_disability SMALLINT,
    pd_other SMALLINT,
    pd_none_disability SMALLINT,
    pd_multi SMALLINT,

    -- Stop circumstances (2024 only)
    person_unhoused SMALLINT,
    passenger_in_vehicle SMALLINT,
    inside_residence SMALLINT,
    welfare_wellness_check SMALLINT,
    tos_vehicular SMALLINT,
    tos_bicycle SMALLINT,
    tos_pedestrian SMALLINT,

    -- Stop reason
    call_for_service SMALLINT,
    reason_for_stop INTEGER,
    rfs_traffic_violation_type INTEGER,
    rfs_traffic_violation_code TEXT,

    -- Reasonable suspicion subcategories
    rfs_rs_off_witness SMALLINT,
    rfs_rs_match_suspect SMALLINT,
    rfs_rs_witness_id SMALLINT,
    rfs_rs_carry_sus_object SMALLINT,
    rfs_rs_actions_indicative SMALLINT,
    rfs_rs_suspect_look SMALLINT,
    rfs_rs_drug_trans SMALLINT,
    rfs_rs_violent_crime SMALLINT,
    rfs_rs_reason_susp SMALLINT,
    rfs_rs_match_vehicle SMALLINT,
    rfs_rs_code TEXT,

    -- Education code
    rfs_ec_discipline_code INTEGER,
    rfs_ec_discipline INTEGER,

    -- Probable cause subcategories (2024 only)
    rfs_pc_off_witness SMALLINT,
    rfs_pc_match_suspect SMALLINT,
    rfs_pc_witness_id SMALLINT,
    rfs_pc_carry_sus_object SMALLINT,
    rfs_pc_actions_indicative SMALLINT,
    rfs_pc_suspect_look SMALLINT,
    rfs_pc_drug_trans SMALLINT,
    rfs_pc_violent_crime SMALLINT,
    rfs_pc_reason_susp SMALLINT,
    rfs_pc_match_vehicle SMALLINT,
    rfs_pc_code TEXT,

    -- Reason given subcategories (2024 only)
    rfs_rg_traffic_moving SMALLINT,
    rfs_rg_traffic_equipment SMALLINT,
    rfs_rg_traffic_non_moving SMALLINT,
    rfs_rg_off_witness SMALLINT,
    rfs_rg_match_suspect SMALLINT,
    rfs_rg_match_vehicle SMALLINT,
    rfs_rg_witness_id SMALLINT,
    rfs_rg_carry_sus_object SMALLINT,
    rfs_rg_actions_indicative SMALLINT,
    rfs_rg_suspect_look SMALLINT,
    rfs_rg_drug_trans SMALLINT,
    rfs_rg_violent_crime SMALLINT,
    rfs_rg_reason_susp SMALLINT,
    rfs_rg_probable_cause SMALLINT,
    rfs_rg_welfare_and_inst SMALLINT,
    rfs_rg_known_parole SMALLINT,
    rfs_rg_outstanding_warrant SMALLINT,
    rfs_rg_truant SMALLINT,
    rfs_rg_consensual_search SMALLINT,
    rfs_rg_discipline SMALLINT,
    rfs_rg_school_policy SMALLINT,
    rfs_rg_not_communicated SMALLINT,

    -- Actions: combined ADS_* (2018-2023 only)
    ads_removed_vehicle_order SMALLINT,
    ads_removed_vehicle_phycontact SMALLINT,
    ads_sobriety_test SMALLINT,
    ads_curb_detent SMALLINT,
    ads_handcuffed SMALLINT,
    ads_patcar_detent SMALLINT,
    ads_canine_search SMALLINT,
    ads_firearm_point SMALLINT,
    ads_firearm_discharge SMALLINT,
    ads_elect_device SMALLINT,
    ads_impact_discharge SMALLINT,
    ads_canine_bite SMALLINT,
    ads_baton SMALLINT,
    ads_chem_spray SMALLINT,
    ads_other_contact SMALLINT,
    ads_photo SMALLINT,
    ads_asked_search_per SMALLINT,
    ads_search_person SMALLINT,
    ads_asked_search_prop SMALLINT,
    ads_search_property SMALLINT,
    ads_prop_seize SMALLINT,
    ads_vehicle_impound SMALLINT,
    ads_written_statement SMALLINT,
    ads_no_actions SMALLINT,
    ads_search_pers_consen SMALLINT,
    ads_search_prop_consen SMALLINT,

    -- Actions: non-force NFA_* (2024 only)
    nfa_written_statement SMALLINT,
    nfa_asked_search_per SMALLINT,
    nfa_asked_search_prop SMALLINT,
    nfa_asked_id_passenger SMALLINT,
    nfa_asked_parole SMALLINT,
    nfa_curb_detent SMALLINT,
    nfa_sobriety_test SMALLINT,
    nfa_patcar_detent SMALLINT,
    nfa_canine_search SMALLINT,
    nfa_photo SMALLINT,
    nfa_removed_vehicle_order SMALLINT,
    nfa_prop_seize SMALLINT,
    nfa_ran_name_passenger SMALLINT,
    nfa_search_person SMALLINT,
    nfa_search_property SMALLINT,
    nfa_terry_frisk SMALLINT,
    nfa_vehicle_impound SMALLINT,
    nfa_none SMALLINT,
    nfa_search_pers_consent SMALLINT,
    nfa_search_prop_consent SMALLINT,

    -- Actions: force OFA_* (2024 only)
    ofa_handcuffed SMALLINT,
    ofa_baton_drawn SMALLINT,
    ofa_baton_used SMALLINT,
    ofa_chem_spray SMALLINT,
    ofa_elect_device_point SMALLINT,
    ofa_elect_device_stun SMALLINT,
    ofa_elect_device_dart SMALLINT,
    ofa_firearm_unholstered SMALLINT,
    ofa_firearm_point SMALLINT,
    ofa_firearm_discharge SMALLINT,
    ofa_impact_projectile_point SMALLINT,
    ofa_impact_projectile_discharge SMALLINT,
    ofa_canine_compliance SMALLINT,
    ofa_canine_bite SMALLINT,
    ofa_removed_vehicle_phycontact SMALLINT,
    ofa_physical_compliance SMALLINT,
    ofa_use_vehicle SMALLINT,
    ofa_none SMALLINT,

    -- Basis for search
    bfs_consent_given SMALLINT,
    bfs_officer_safety SMALLINT,
    bfs_search_warrant SMALLINT,
    bfs_parole SMALLINT,
    bfs_suspect_weapon SMALLINT,
    bfs_visible_contraband SMALLINT,
    bfs_odor_contraband SMALLINT,
    bfs_canine_detect SMALLINT,
    bfs_evidence SMALLINT,
    bfs_incident SMALLINT,
    bfs_exigent_circum SMALLINT,
    bfs_vehicle_invent SMALLINT,
    bfs_school_policy SMALLINT,

    -- Consent type (2024 only)
    ctp_verbal SMALLINT,
    ctp_written SMALLINT,
    ctp_implied SMALLINT,

    -- Contraband/evidence discovered
    ced_none_contraband SMALLINT,
    ced_firearm SMALLINT,
    ced_ammunition SMALLINT,
    ced_weapon SMALLINT,
    ced_drugs SMALLINT,
    ced_alcohol SMALLINT,
    ced_money SMALLINT,
    ced_drug_paraphernalia SMALLINT,
    ced_stolen_prop SMALLINT,
    ced_elect_device SMALLINT,
    ced_other_contraband SMALLINT,

    -- Basis for property seizure
    bps_safekeeping SMALLINT,
    bps_contraband SMALLINT,
    bps_evidence SMALLINT,
    bps_impound_vehicle SMALLINT,
    bps_abandon_prop SMALLINT,
    bps_violate_school SMALLINT,

    -- Type of property seized
    tps_firearm SMALLINT,
    tps_ammunition SMALLINT,
    tps_weapon SMALLINT,
    tps_drugs SMALLINT,
    tps_alcohol SMALLINT,
    tps_money SMALLINT,
    tps_drug_paraphernalia SMALLINT,
    tps_stolen_prop SMALLINT,
    tps_cellphone SMALLINT,
    tps_vehicle SMALLINT,
    tps_contraband SMALLINT,

    -- Result of stop
    ros_no_action SMALLINT,
    ros_warning SMALLINT,
    ros_written_warning SMALLINT,
    ros_verbal_warning SMALLINT,
    ros_citation SMALLINT,
    ros_in_field_cite_release SMALLINT,
    ros_custodial_warrant SMALLINT,
    ros_custodial_without_warrant SMALLINT,
    ros_field_interview_card SMALLINT,
    ros_noncriminal_transport SMALLINT,
    ros_contact_legal_guardian SMALLINT,
    ros_psych_hold SMALLINT,
    ros_us_homeland SMALLINT,
    ros_referral_school_admin SMALLINT,
    ros_referral_school_counselor SMALLINT,

    -- Result of stop: CJIS codes
    ros_warning_cds TEXT,
    ros_verbal_warning_cds TEXT,
    ros_written_warning_cds TEXT,
    ros_citation_cds TEXT,
    ros_in_field_cite_release_cds TEXT,
    ros_custodial_wout_warrant_cds TEXT
);

-- ============================================================
-- Indexes on stops
-- ============================================================
CREATE INDEX idx_stops_agency_year ON stops (agency_ori, data_year);
CREATE INDEX idx_stops_year ON stops (data_year);
CREATE INDEX idx_stops_agency ON stops (agency_ori);

-- ============================================================
-- Agencies dimension table
-- ============================================================
CREATE TABLE agencies (
    agency_ori TEXT PRIMARY KEY,
    agency_name TEXT NOT NULL,
    county TEXT,
    first_year SMALLINT NOT NULL,
    last_year SMALLINT NOT NULL,
    total_person_stops BIGINT NOT NULL
);

INSERT INTO agencies (agency_ori, agency_name, county, first_year, last_year, total_person_stops)
SELECT
    agency_ori,
    -- Use the most recent agency name
    (ARRAY_AGG(agency_name ORDER BY data_year DESC))[1] AS agency_name,
    -- Use most recent county
    (ARRAY_AGG(county ORDER BY data_year DESC))[1] AS county,
    MIN(data_year) AS first_year,
    MAX(data_year) AS last_year,
    COUNT(*) AS total_person_stops
FROM stops
WHERE agency_ori IS NOT NULL
GROUP BY agency_ori;

CREATE INDEX idx_agencies_name ON agencies USING gin (agency_name gin_trgm_ops);

-- ============================================================
-- Materialized view: agency × year × race
-- ============================================================
CREATE MATERIALIZED VIEW mv_agency_year_race AS
SELECT
    agency_ori,
    data_year,
    rae_full AS race_code,
    COUNT(*) AS n_person_stops,
    COUNT(DISTINCT doj_record_id) AS n_stops,

    -- Was searched (harmonized across eras)
    SUM(CASE
        WHEN data_year < 2024 THEN
            GREATEST(COALESCE(ads_search_person, 0), COALESCE(ads_search_property, 0))
        ELSE
            GREATEST(COALESCE(nfa_search_person, 0), COALESCE(nfa_search_property, 0),
                     COALESCE(nfa_terry_frisk, 0))
    END) AS n_searched,

    -- Force used (harmonized across eras)
    SUM(CASE
        WHEN data_year < 2024 THEN GREATEST(
            COALESCE(ads_handcuffed, 0), COALESCE(ads_firearm_point, 0),
            COALESCE(ads_firearm_discharge, 0), COALESCE(ads_elect_device, 0),
            COALESCE(ads_impact_discharge, 0), COALESCE(ads_canine_bite, 0),
            COALESCE(ads_baton, 0), COALESCE(ads_chem_spray, 0),
            COALESCE(ads_other_contact, 0))
        ELSE GREATEST(
            COALESCE(ofa_handcuffed, 0), COALESCE(ofa_firearm_point, 0),
            COALESCE(ofa_firearm_discharge, 0), COALESCE(ofa_baton_used, 0),
            COALESCE(ofa_chem_spray, 0), COALESCE(ofa_canine_bite, 0),
            COALESCE(ofa_elect_device_stun, 0), COALESCE(ofa_elect_device_dart, 0),
            COALESCE(ofa_impact_projectile_discharge, 0),
            COALESCE(ofa_physical_compliance, 0), COALESCE(ofa_use_vehicle, 0),
            COALESCE(ofa_removed_vehicle_phycontact, 0))
    END) AS n_force_used,

    -- Arrested
    SUM(GREATEST(COALESCE(ros_custodial_warrant, 0),
                 COALESCE(ros_custodial_without_warrant, 0))) AS n_arrested,

    -- Cited
    SUM(GREATEST(COALESCE(ros_citation, 0),
                 COALESCE(ros_in_field_cite_release, 0))) AS n_cited,

    -- Warned (harmonized)
    SUM(CASE
        WHEN data_year < 2024 THEN COALESCE(ros_warning, 0)
        ELSE GREATEST(COALESCE(ros_written_warning, 0),
                      COALESCE(ros_verbal_warning, 0))
    END) AS n_warned,

    -- No action
    SUM(COALESCE(ros_no_action, 0)) AS n_no_action,

    -- Contraband found (among searched)
    SUM(CASE
        WHEN CASE
            WHEN data_year < 2024 THEN
                GREATEST(COALESCE(ads_search_person, 0), COALESCE(ads_search_property, 0))
            ELSE
                GREATEST(COALESCE(nfa_search_person, 0), COALESCE(nfa_search_property, 0),
                         COALESCE(nfa_terry_frisk, 0))
        END = 1
        THEN GREATEST(
            COALESCE(ced_firearm, 0), COALESCE(ced_ammunition, 0),
            COALESCE(ced_weapon, 0), COALESCE(ced_drugs, 0),
            COALESCE(ced_alcohol, 0), COALESCE(ced_money, 0),
            COALESCE(ced_drug_paraphernalia, 0), COALESCE(ced_stolen_prop, 0),
            COALESCE(ced_elect_device, 0), COALESCE(ced_other_contraband, 0))
        ELSE 0
    END) AS n_contraband_found,

    -- No contraband (among searched)
    SUM(CASE
        WHEN CASE
            WHEN data_year < 2024 THEN
                GREATEST(COALESCE(ads_search_person, 0), COALESCE(ads_search_property, 0))
            ELSE
                GREATEST(COALESCE(nfa_search_person, 0), COALESCE(nfa_search_property, 0),
                         COALESCE(nfa_terry_frisk, 0))
        END = 1
        THEN COALESCE(ced_none_contraband, 0)
        ELSE 0
    END) AS n_no_contraband

FROM stops
WHERE agency_ori IS NOT NULL AND rae_full IS NOT NULL
GROUP BY agency_ori, data_year, rae_full;

CREATE INDEX idx_mv_ayr_agency ON mv_agency_year_race (agency_ori);
CREATE INDEX idx_mv_ayr_agency_year ON mv_agency_year_race (agency_ori, data_year);

-- ============================================================
-- Materialized view: agency × year × gender
-- ============================================================
CREATE MATERIALIZED VIEW mv_agency_year_gender AS
SELECT
    agency_ori,
    data_year,
    g_full AS gender_code,
    COUNT(*) AS n_person_stops,
    COUNT(DISTINCT doj_record_id) AS n_stops,

    SUM(CASE
        WHEN data_year < 2024 THEN
            GREATEST(COALESCE(ads_search_person, 0), COALESCE(ads_search_property, 0))
        ELSE
            GREATEST(COALESCE(nfa_search_person, 0), COALESCE(nfa_search_property, 0),
                     COALESCE(nfa_terry_frisk, 0))
    END) AS n_searched,

    SUM(CASE
        WHEN data_year < 2024 THEN GREATEST(
            COALESCE(ads_handcuffed, 0), COALESCE(ads_firearm_point, 0),
            COALESCE(ads_firearm_discharge, 0), COALESCE(ads_elect_device, 0),
            COALESCE(ads_impact_discharge, 0), COALESCE(ads_canine_bite, 0),
            COALESCE(ads_baton, 0), COALESCE(ads_chem_spray, 0),
            COALESCE(ads_other_contact, 0))
        ELSE GREATEST(
            COALESCE(ofa_handcuffed, 0), COALESCE(ofa_firearm_point, 0),
            COALESCE(ofa_firearm_discharge, 0), COALESCE(ofa_baton_used, 0),
            COALESCE(ofa_chem_spray, 0), COALESCE(ofa_canine_bite, 0),
            COALESCE(ofa_elect_device_stun, 0), COALESCE(ofa_elect_device_dart, 0),
            COALESCE(ofa_impact_projectile_discharge, 0),
            COALESCE(ofa_physical_compliance, 0), COALESCE(ofa_use_vehicle, 0),
            COALESCE(ofa_removed_vehicle_phycontact, 0))
    END) AS n_force_used,

    SUM(GREATEST(COALESCE(ros_custodial_warrant, 0),
                 COALESCE(ros_custodial_without_warrant, 0))) AS n_arrested,

    SUM(GREATEST(COALESCE(ros_citation, 0),
                 COALESCE(ros_in_field_cite_release, 0))) AS n_cited,

    SUM(CASE
        WHEN data_year < 2024 THEN COALESCE(ros_warning, 0)
        ELSE GREATEST(COALESCE(ros_written_warning, 0),
                      COALESCE(ros_verbal_warning, 0))
    END) AS n_warned,

    SUM(COALESCE(ros_no_action, 0)) AS n_no_action

FROM stops
WHERE agency_ori IS NOT NULL AND g_full IS NOT NULL
GROUP BY agency_ori, data_year, g_full;

CREATE INDEX idx_mv_ayg_agency ON mv_agency_year_gender (agency_ori);

-- ============================================================
-- Materialized view: agency × year × age group
-- ============================================================
CREATE MATERIALIZED VIEW mv_agency_year_age AS
SELECT
    agency_ori,
    data_year,
    age_group,
    COUNT(*) AS n_person_stops,
    COUNT(DISTINCT doj_record_id) AS n_stops,

    SUM(CASE
        WHEN data_year < 2024 THEN
            GREATEST(COALESCE(ads_search_person, 0), COALESCE(ads_search_property, 0))
        ELSE
            GREATEST(COALESCE(nfa_search_person, 0), COALESCE(nfa_search_property, 0),
                     COALESCE(nfa_terry_frisk, 0))
    END) AS n_searched,

    SUM(CASE
        WHEN data_year < 2024 THEN GREATEST(
            COALESCE(ads_handcuffed, 0), COALESCE(ads_firearm_point, 0),
            COALESCE(ads_firearm_discharge, 0), COALESCE(ads_elect_device, 0),
            COALESCE(ads_impact_discharge, 0), COALESCE(ads_canine_bite, 0),
            COALESCE(ads_baton, 0), COALESCE(ads_chem_spray, 0),
            COALESCE(ads_other_contact, 0))
        ELSE GREATEST(
            COALESCE(ofa_handcuffed, 0), COALESCE(ofa_firearm_point, 0),
            COALESCE(ofa_firearm_discharge, 0), COALESCE(ofa_baton_used, 0),
            COALESCE(ofa_chem_spray, 0), COALESCE(ofa_canine_bite, 0),
            COALESCE(ofa_elect_device_stun, 0), COALESCE(ofa_elect_device_dart, 0),
            COALESCE(ofa_impact_projectile_discharge, 0),
            COALESCE(ofa_physical_compliance, 0), COALESCE(ofa_use_vehicle, 0),
            COALESCE(ofa_removed_vehicle_phycontact, 0))
    END) AS n_force_used,

    SUM(GREATEST(COALESCE(ros_custodial_warrant, 0),
                 COALESCE(ros_custodial_without_warrant, 0))) AS n_arrested,

    SUM(GREATEST(COALESCE(ros_citation, 0),
                 COALESCE(ros_in_field_cite_release, 0))) AS n_cited,

    SUM(CASE
        WHEN data_year < 2024 THEN COALESCE(ros_warning, 0)
        ELSE GREATEST(COALESCE(ros_written_warning, 0),
                      COALESCE(ros_verbal_warning, 0))
    END) AS n_warned,

    SUM(COALESCE(ros_no_action, 0)) AS n_no_action

FROM stops
WHERE agency_ori IS NOT NULL AND age_group IS NOT NULL
GROUP BY agency_ori, data_year, age_group;

CREATE INDEX idx_mv_aya_agency ON mv_agency_year_age (agency_ori);

