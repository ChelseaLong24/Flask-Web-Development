from flask import Blueprint, render_template, request, flash
from .models import Carrier, Country, CountryResidenceMapping, CarrierInfo, USNexus, USNexusCarrierMapping, NRA, NRAPresenceTypeMapping, NRAFinancialPresence, NRAPhysicalPresence, SSN_TIN_document, Document_carrier_mapping, Approved_Ownership_Structure, Approved_Ownership_Structure_carrier_mapping, Foreign_Travel_Rules_for_USCitizens, Outbound_requirement, Inbound_requirement, ExPats_outbound_mapping, ExPats_Inbound_mapping
from . import db

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    results = []
    citizenship_values = []
    visa_values = []

    # Default values for input fields
    country_name = ''
    city_name = ''
    region_name = ''
    citizenship = ''
    visa = ''

    if request.method == 'POST':
        country_name = request.form.get('country')
        city_name = request.form.get('city')
        region_name = request.form.get('region')
        citizenship = request.form.get('citizenship')
        visa = request.form.get('visa')
        
        query = db.session.query(
            Carrier.Insurance_company_name,
            Carrier.Internal_code,
            #Country.Country,
            #Country.City,
            #Country.Region,
            Country.Include_flag,
            CountryResidenceMapping.Notes.label('CountryResidence_Notes'),
            USNexus.Nexus_Conditions,
            USNexus.Nexus_Notes,
            #NRA.US_Nexus_flag,
            NRA.Other_policy_related,
            NRA.Minimum_policy_face_amount_USD_Denominated,
            NRA.Minimum_global_net_worth_USD_Denominated,
            #NRA.Age_related,
            NRA.Citizenship_visa_specified,
            NRA.Notes.label('NRA_Notes'),
            NRAPhysicalPresence.General,
            NRAPhysicalPresence.Min_in_the_us_for_prior_12_months_annually_month,
            NRAPhysicalPresence.Min_in_the_us_for_prior_24_months_annually_month,
            NRAPhysicalPresence.Min_in_the_us_for_prior_48_months_annually_month,
            NRAPhysicalPresence.Min_in_the_us_annually_month,
            NRAPhysicalPresence.Min_spend_outside_annually_month,
            #NRAPhysicalPresence.Citizenship,
            #NRAPhysicalPresence.Visa,
            NRAPhysicalPresence.Max_total_time_been_in_the_us_year,
            NRAFinancialPresence.Personal_insurance_flag,
            NRAFinancialPresence.Need_for_US_based_coverage_flag,
            NRAFinancialPresence.Determining_justified_amounts,
            NRAFinancialPresence.Bank_account_min_opened_time_prior_to_app_month,
            #NRAFinancialPresence.Bank_account_info,
            #NRAFinancialPresence.Bank_balance,
            #NRAFinancialPresence.Wealth,
            NRAFinancialPresence.Time_of_verifiable_US_assets_in_the_US_month,
            NRAFinancialPresence.Verifiable_US_assets_in_the_US_million
        ).outerjoin(CountryResidenceMapping, CountryResidenceMapping.Carrier_GUID_FK == Carrier.Carrier_GUID_PK) \
         .outerjoin(Country, CountryResidenceMapping.Country_GUID_FK == Country.Country_GUID_PK) \
         .outerjoin(NRA, NRA.Carrier_GUID_FK == Carrier.Carrier_GUID_PK) \
         .outerjoin(NRAPresenceTypeMapping, NRAPresenceTypeMapping.NRA_GUID_FK == NRA.NRA_GUID_PK)\
         .outerjoin(NRAPhysicalPresence, NRAPhysicalPresence.Physical_presence_GUID_PK == NRAPresenceTypeMapping.Physical_presence_GUID_FK) \
         .outerjoin(NRAFinancialPresence, NRAFinancialPresence.Financial_presence_GUID_PK == NRAPresenceTypeMapping.Financial_presence_GUID_FK) \
         .outerjoin(USNexusCarrierMapping, USNexusCarrierMapping.Carrier_GUID_FK == Carrier.Carrier_GUID_PK) \
         .outerjoin(USNexus, USNexusCarrierMapping.US_Nexus_GUID_FK == USNexus.US_Nexus_GUID_PK)
        
        if country_name:
            query = query.filter(Country.Country == country_name)
        if city_name:
            query = query.filter(Country.City.like(f'%{city_name}%'))
        if region_name:
            query = query.filter(Country.Region.like(f'%{region_name}%'))
        if citizenship:
            query = query.filter(NRAPhysicalPresence.Citizenship == citizenship)
        if visa:
            query = query.filter(NRAPhysicalPresence.Visa == visa)

        results = query.order_by(Carrier.Insurance_company_name).all()

        if not results:
            flash('No results found!', category='error')

    citizenship_values = db.session.query(NRAPhysicalPresence.Citizenship) \
        .filter(NRAPhysicalPresence.Citizenship.isnot(None)) \
        .distinct().all()
    visa_values = db.session.query(NRAPhysicalPresence.Visa) \
        .filter(NRAPhysicalPresence.Visa.isnot(None)) \
        .distinct().all()
    
    citizenship_values = [value[0] for value in citizenship_values]
    visa_values = [value[0] for value in visa_values]

    return render_template(
        "home.html", 
        results=results, 
        citizenship_values=citizenship_values, 
        visa_values=visa_values,
        country_name=country_name,
        city_name=city_name,
        region_name=region_name,
        citizenship=citizenship,
        visa=visa
    )

# Debug output
    '''for result in results:
            print(f'Raw Include_flag: {result.Include_flag}')
            print(f'Converted Include_flag: {bool(result.Include_flag)}')'''

            # Convert query results to dictionary and update Include_flag
    '''results = [
                {
                    'Insurance_company_name': res.Insurance_company_name,
                    'Internal_code': res.Internal_code,
                    'Area': res.Area,
                    'Country': res.Country,
                    'City': res.City,
                    'Region': res.Region,
                    'Include_flag': bool(res.Include_flag),
                    'Notes': res.Notes
                } for res in results
            ]'''

            # Debug output
    '''for result in results:
                print(f'Include_flag: {result["Include_flag"]}') (type: {type(result["Include_flag"])})')'''            



@views.route('/admin', methods=['GET', 'POST'])
def admin():
    results = []
    carrier_values = [carrier[0] for carrier in db.session.query(Carrier.Insurance_company_name).distinct().all()]
    selected_carrier = None

    if request.method == 'POST':
        selected_carrier = request.form.get('carrier')

        if selected_carrier:
            results = db.session.query(
                Carrier.Insurance_company_name,
                Carrier.Internal_code,
                Carrier.Alias_used_name,
                Carrier.Branch,
                Country.Country,
                Country.City,
                Country.Region,
                Country.Include_flag,
                CountryResidenceMapping.Country_category,
                CountryResidenceMapping.Notes.label("CountryResidence_Notes"),
                CarrierInfo.Date_last_updated,
                CarrierInfo.Date_last_policy_inforce,
                CarrierInfo.Financial_ratings_institution,
                CarrierInfo.Ratings,
                CarrierInfo.Notes.label("CarrierInfo_Notes"),
                USNexus.Nexus_Conditions,
                USNexus.Nexus_Notes,
                NRA.US_Nexus_flag,
                NRA.Other_policy_related,
                NRA.Minimum_policy_face_amount_USD_Denominated,
                NRA.Minimum_global_net_worth_USD_Denominated,
                NRA.Age_related,
                NRA.Citizenship_visa_specified,
                NRA.Notes.label("NRA_Notes"),
                NRAPhysicalPresence.General,
                NRAPhysicalPresence.Min_in_the_us_for_prior_12_months_annually_month,
                NRAPhysicalPresence.Min_in_the_us_for_prior_24_months_annually_month,
                NRAPhysicalPresence.Min_in_the_us_for_prior_48_months_annually_month,
                NRAPhysicalPresence.Min_in_the_us_annually_month,
                NRAPhysicalPresence.Min_spend_outside_annually_month,
                NRAPhysicalPresence.Citizenship.label("Physical_Citizenship"),
                NRAPhysicalPresence.Visa,
                NRAPhysicalPresence.Max_total_time_been_in_the_us_year,
                NRAFinancialPresence.Citizenship.label("Financial_Citizenship"),
                NRAFinancialPresence.Residence,
                NRAFinancialPresence.Personal_insurance_flag,
                NRAFinancialPresence.Need_for_US_based_coverage_flag,
                NRAFinancialPresence.Determining_justified_amounts,
                NRAFinancialPresence.Bank_account_min_opened_time_prior_to_app_month,
                NRAFinancialPresence.Bank_account_info,
                NRAFinancialPresence.Bank_balance,
                NRAFinancialPresence.Wealth,
                NRAFinancialPresence.Time_of_verifiable_US_assets_in_the_US_month,
                NRAFinancialPresence.Verifiable_US_assets_in_the_US_million,
                SSN_TIN_document.Document_name,
                Document_carrier_mapping.Document_notes,
                Approved_Ownership_Structure.Ownership_Structure,
                Approved_Ownership_Structure_carrier_mapping.Ownership_Structure_carrier_notes,
                Foreign_Travel_Rules_for_USCitizens.Minimum_time_spend_outside_of_the_US_Per_Year_week,
                Foreign_Travel_Rules_for_USCitizens.Foreign_country_specified,
                Foreign_Travel_Rules_for_USCitizens.Notes.label("Travel_Notes"),
                ExPats_outbound_mapping.Identities,
                ExPats_outbound_mapping.Acceptable_residing_country,
                ExPats_outbound_mapping.Foreign_living_condition,
                ExPats_outbound_mapping.Exclusion,
                ExPats_Inbound_mapping.Identities.label("Inbound_Identities"),
                ExPats_Inbound_mapping.Citizenship.label("Inbound_Citizenship"),
                ExPats_Inbound_mapping.Citizenship_exclusion_flag,
                ExPats_Inbound_mapping.Acceptable_visa_status_type,
                ExPats_Inbound_mapping.Min_time_reside_in_us_per_year_month,
                ExPats_Inbound_mapping.Min_time_reside_in_us_month,
                ExPats_Inbound_mapping.Continue_reside_flag,
                ExPats_Inbound_mapping.Nexus_flag,
                ExPats_Inbound_mapping.Max_foreign_travel_month,
                ExPats_Inbound_mapping.Policy_type.label("Inbound_Policy_type"),
                ExPats_Inbound_mapping.Notes.label("Inbound_Notes")
            ).outerjoin(
                CountryResidenceMapping, Carrier.Carrier_GUID_PK == CountryResidenceMapping.Carrier_GUID_FK
            ).outerjoin(
                Country, CountryResidenceMapping.Country_GUID_FK == Country.Country_GUID_PK
            ).outerjoin(
                CarrierInfo, Carrier.Carrier_GUID_PK == CarrierInfo.Carrier_GUID_FK
            ).outerjoin(
                USNexusCarrierMapping, Carrier.Carrier_GUID_PK == USNexusCarrierMapping.Carrier_GUID_FK
            ).outerjoin(
                USNexus, USNexus.US_Nexus_GUID_PK == USNexusCarrierMapping.US_Nexus_GUID_FK
            ).outerjoin(
                NRA, Carrier.Carrier_GUID_PK == NRA.Carrier_GUID_FK
            ).outerjoin(
                NRAPresenceTypeMapping, NRA.NRA_GUID_PK == NRAPresenceTypeMapping.NRA_GUID_FK
            ).outerjoin(
                NRAFinancialPresence, NRAPresenceTypeMapping.Financial_presence_GUID_FK == NRAFinancialPresence.Financial_presence_GUID_PK
            ).outerjoin(
                NRAPhysicalPresence, NRAPresenceTypeMapping.Physical_presence_GUID_FK == NRAPhysicalPresence.Physical_presence_GUID_PK
            ).outerjoin(
                Document_carrier_mapping, Carrier.Carrier_GUID_PK == Document_carrier_mapping.Carrier_GUID_FK
            ).outerjoin(
                SSN_TIN_document, Document_carrier_mapping.Document_GUID_FK == SSN_TIN_document.Document_GUID_PK
            ).outerjoin(
                Approved_Ownership_Structure_carrier_mapping, Carrier.Carrier_GUID_PK == Approved_Ownership_Structure_carrier_mapping.Carrier_GUID_FK
            ).outerjoin(
                Approved_Ownership_Structure, Approved_Ownership_Structure_carrier_mapping.Approved_Ownership_Structure_GUID_FK == Approved_Ownership_Structure.Approved_Ownership_Structure_GUID_PK
            ).outerjoin(
                Foreign_Travel_Rules_for_USCitizens, Carrier.Carrier_GUID_PK == Foreign_Travel_Rules_for_USCitizens.Carrier_GUID_FK
            ).outerjoin(
                ExPats_outbound_mapping, Carrier.Carrier_GUID_PK == ExPats_outbound_mapping.Carrier_GUID_FK
            ).outerjoin(
                Outbound_requirement, Outbound_requirement.Outbound_requirement_GUID_PK == ExPats_outbound_mapping.Outbound_requirement_GUID_FK
            ).outerjoin(
                ExPats_Inbound_mapping, Carrier.Carrier_GUID_PK == ExPats_Inbound_mapping.Carrier_GUID_FK
            ).outerjoin(
                Inbound_requirement, Inbound_requirement.Inbound_requirement_GUID_PK == ExPats_Inbound_mapping.Inbound_requirement_GUID_FK
            ).filter(
                Carrier.Insurance_company_name == selected_carrier
            ).all()

            if not results:
                flash('No results found!', category='warning')

    return render_template(
        'admin.html', 
        results=results, 
        carrier_values=carrier_values, 
        selected_carrier=selected_carrier
    )