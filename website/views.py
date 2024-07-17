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
