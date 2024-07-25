from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Carrier, Country, CountryResidenceMapping, CarrierInfo, USNexus, USNexusCarrierMapping, NRA, NRAPresenceTypeMapping, NRAFinancialPresence, \
                    NRAPhysicalPresence, SSN_TIN_document, Document_carrier_mapping, Approved_Ownership_Structure, Approved_Ownership_Structure_carrier_mapping, \
                    Foreign_Travel_Rules_for_USCitizens, Outbound_requirement, Inbound_requirement, ExPats_outbound_mapping, ExPats_Inbound_mapping, FeatureRegistry
from . import db
import uuid

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
    selected_feature = None

    feature_dict = {
        'Insurance_company_name': 'Insurance Company Name',
        'Alias_used_name': 'Alias Used Name',
        'Branch': 'Branch',
        'Include_flag': 'Include Flag',
        'Country_category': 'Country Category',
        'Notes': 'Notes',
        'Nexus_Conditions': 'Nexus Conditions',
        'Nexus_Notes': 'Nexus Notes',
        'US_Nexus_flag': 'US Nexus Flag',
        'Other_policy_related': 'Other Policy Related',
        'Minimum_policy_face_amount_USD_Denominated': 'Minimum Policy Face Amount (USD Denominated)',
        'Minimum_global_net_worth_USD_Denominated': 'Minimum Global Net Worth (USD Denominated)',
        'Age_related': 'Age Related',
        'Citizenship_visa_specified': 'Citizenship Visa Specified',
        'General': 'General',
        'Min_in_the_us_for_prior_12_months_annually_month': 'Min in US for Prior 12 Months (Annually)',
        'Min_in_the_us_for_prior_24_months_annually_month': 'Min in US for Prior 24 Months (Annually)',
        'Min_in_the_us_for_prior_48_months_annually_month': 'Min in US for Prior 48 Months (Annually)',
        'Min_in_the_us_annually_month': 'Min in US Annually',
        'Min_spend_outside_annually_month': 'Min Spend Outside Annually',
        'Physical_Citizenship': 'Physical Citizenship',
        'Visa': 'Visa',
        'Max_total_time_been_in_the_us_year': 'Max Total Time Been in US (Year)',
        'Financial_Citizenship': 'Financial Citizenship',
        'Residence': 'Residence',
        'Personal_insurance_flag': 'Personal Insurance Flag',
        'Need_for_US_based_coverage_flag': 'Need for US Based Coverage Flag',
        'Determining_justified_amounts': 'Determining Justified Amounts',
        'Bank_account_min_opened_time_prior_to_app_month': 'Bank Account Min Opened Time Prior to App (Month)',
        'Bank_account_info': 'Bank Account Info',
        'Bank_balance': 'Bank Balance',
        'Wealth': 'Wealth',
        'Time_of_verifiable_US_assets_in_the_US_month': 'Time of Verifiable US Assets in the US (Month)',
        'Verifiable_US_assets_in_the_US_million': 'Verifiable US Assets in the US (Million)',
        'Document_name': 'Document Name',
        'Document_notes': 'Document Notes',
        'Ownership_Structure': 'Ownership Structure',
        'Ownership_Structure_carrier_notes': 'Ownership Structure Carrier Notes',
        'Minimum_time_spend_outside_of_the_US_Per_Year_week': 'Minimum Time Spend Outside of the US (Per Year - Week)',
        'Foreign_country_specified': 'Foreign Country Specified',
        'Travel_Notes': 'Travel Notes',
        'Identities': 'Identities',
        'Acceptable_residing_country': 'Acceptable Residing Country',
        'Foreign_living_condition': 'Foreign Living Condition',
        'Exclusion': 'Exclusion',
        'Inbound_Identities': 'Inbound Identities',
        'Inbound_Citizenship': 'Inbound Citizenship',
        'Citizenship_exclusion_flag': 'Citizenship Exclusion Flag',
        'Acceptable_visa_status_type': 'Acceptable Visa Status Type',
        'Min_time_reside_in_us_per_year_month': 'Min Time Reside in US per Year (Month)',
        'Min_time_reside_in_us_month': 'Min Time Reside in US (Month)',
        'Continue_reside_flag': 'Continue Reside Flag',
        'Nexus_flag': 'Nexus Flag',
        'Max_foreign_travel_month': 'Max Foreign Travel (Month)',
        'Inbound_Policy_type': 'Inbound Policy Type',
        'Inbound_Notes': 'Inbound Notes'
    }

    # Get added features from FeatureRegistry and integrate into feature_dict
    additional_features = db.session.query(FeatureRegistry).all()
    for feature in additional_features:
        if feature.feature_name not in feature_dict:
            feature_dict[feature.feature_name] = feature.feature_name

    if request.method == 'POST':
        selected_carrier = request.form.get('carrier')
        selected_feature = request.form.get('feature')

        if selected_carrier:
            subquery = db.session.query(
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
            ).distinct().subquery()

            query = db.session.query(
                subquery.c.Insurance_company_name,
                subquery.c.Internal_code,
                subquery.c.Alias_used_name,
                subquery.c.Branch,
                subquery.c.Country,
                subquery.c.City,
                subquery.c.Region,
                subquery.c.Include_flag,
                subquery.c.Country_category,
                subquery.c.CountryResidence_Notes,
                subquery.c.Date_last_updated,
                subquery.c.Date_last_policy_inforce,
                subquery.c.Financial_ratings_institution,
                subquery.c.Ratings,
                subquery.c.CarrierInfo_Notes,
                subquery.c.Nexus_Conditions,
                subquery.c.Nexus_Notes,
                subquery.c.US_Nexus_flag,
                subquery.c.Other_policy_related,
                subquery.c.Minimum_policy_face_amount_USD_Denominated,
                subquery.c.Minimum_global_net_worth_USD_Denominated,
                subquery.c.Age_related,
                subquery.c.Citizenship_visa_specified,
                subquery.c.NRA_Notes,
                subquery.c.General,
                subquery.c.Min_in_the_us_for_prior_12_months_annually_month,
                subquery.c.Min_in_the_us_for_prior_24_months_annually_month,
                subquery.c.Min_in_the_us_for_prior_48_months_annually_month,
                subquery.c.Min_in_the_us_annually_month,
                subquery.c.Min_spend_outside_annually_month,
                subquery.c.Physical_Citizenship,
                subquery.c.Visa,
                subquery.c.Max_total_time_been_in_the_us_year,
                subquery.c.Financial_Citizenship,
                subquery.c.Residence,
                subquery.c.Personal_insurance_flag,
                subquery.c.Need_for_US_based_coverage_flag,
                subquery.c.Determining_justified_amounts,
                subquery.c.Bank_account_min_opened_time_prior_to_app_month,
                subquery.c.Bank_account_info,
                subquery.c.Bank_balance,
                subquery.c.Wealth,
                subquery.c.Time_of_verifiable_US_assets_in_the_US_month,
                subquery.c.Verifiable_US_assets_in_the_US_million,
                subquery.c.Document_name,
                subquery.c.Document_notes,
                subquery.c.Ownership_Structure,
                subquery.c.Ownership_Structure_carrier_notes,
                subquery.c.Minimum_time_spend_outside_of_the_US_Per_Year_week,
                subquery.c.Foreign_country_specified,
                subquery.c.Travel_Notes,
                subquery.c.Identities,
                subquery.c.Acceptable_residing_country,
                subquery.c.Foreign_living_condition,
                subquery.c.Exclusion,
                subquery.c.Inbound_Identities,
                subquery.c.Inbound_Citizenship,
                subquery.c.Citizenship_exclusion_flag,
                subquery.c.Acceptable_visa_status_type,
                subquery.c.Min_time_reside_in_us_per_year_month,
                subquery.c.Min_time_reside_in_us_month,
                subquery.c.Continue_reside_flag,
                subquery.c.Nexus_flag,
                subquery.c.Max_foreign_travel_month,
                subquery.c.Inbound_Policy_type,
                subquery.c.Inbound_Notes
            ).filter(
                subquery.c.Insurance_company_name == selected_carrier
)

            if selected_feature:
                query = query.add_columns(
                    getattr(subquery.c, selected_feature, None)
                )

            results = query.all()

            results = [
                {**dict(row._asdict()), selected_feature: dict(row._asdict()).get(selected_feature)}
                for row in results
            ]

            if not results:
                flash('No results found!', category='warning')

    return render_template(
        'admin.html', 
        results=results, 
        carrier_values=carrier_values, 
        selected_carrier=selected_carrier,
        selected_feature=selected_feature,
        feature_dict=feature_dict
    )


@views.route('/update', methods=['POST'])
def update():
    selected_feature = request.form.get('feature')

    if not selected_feature:
        flash('No feature selected for update.', category='warning')
        return redirect(url_for('views.admin'))

    for key, value in request.form.items():
        if key.startswith(f'{selected_feature}_'):
            index = key.split('_')[1]
            carrier_guid_pk = request.form.get(f'Carrier_GUID_PK_{index}')
            feature_value = value

            carrier = Carrier.query.get(carrier_guid_pk)
            if carrier:
                setattr(carrier, selected_feature, feature_value)
                db.session.commit()

    flash('Changes saved successfully!', category='success')
    return redirect(url_for('views.admin'))

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

@views.route('/add-feature', methods=['GET', 'POST'])
def add_feature():
    carrier_values = [carrier[0] for carrier in db.session.query(Carrier.Insurance_company_name).distinct().all()]

    if request.method == 'POST':
        selected_carrier = request.form.get('carrier')
        new_feature_name = request.form.get('new_feature_name')
        new_feature_value = request.form.get('new_feature_value')

        if selected_carrier and new_feature_name and new_feature_value:
            metadata = MetaData()
            new_table_name = f"{selected_carrier}_{new_feature_name}"
            new_table = Table(new_table_name, metadata,\
                              Column('id', Integer, primary_key=True),\
                              Column('carrier', String(100)),\
                              Column('feature_name', String(100)),\
                              Column('feature_value', String(255))\
                              )

            metadata.create_all(db.engine)

            insert_query = new_table.insert().values(
                carrier=selected_carrier,
                feature_name=new_feature_name,
                feature_value=new_feature_value
            )
            db.session.execute(insert_query)
            db.session.commit()

            #Save to FeatureRegistry
            new_feature = FeatureRegistry(
                carrier=selected_carrier,
                feature_name=new_feature_name,
                feature_value=new_feature_value
            )
            db.session.add(new_feature)
            db.session.commit()

            flash('Feature added successfully!', category='success')
            return redirect(url_for('views.admin'))

    return render_template('add_feature.html', carrier_values=carrier_values)

@views.route('/add-carrier', methods=['GET', 'POST'])
def add_carrier():

    carrier_values = [carrier[0] for carrier in db.session.query(Carrier.Insurance_company_name).distinct().all()]

    feature_dict = {
        'Insurance_company_name': 'Insurance Company Name',
        'Alias_used_name': 'Alias Used Name',
        'Branch': 'Branch',
        'Include_flag': 'Include Flag',
        'Country_category': 'Country Category',
        'Notes': 'Notes',
        'Nexus_Conditions': 'Nexus Conditions',
        'Nexus_Notes': 'Nexus Notes',
        'US_Nexus_flag': 'US Nexus Flag',
        'Other_policy_related': 'Other Policy Related',
        'Minimum_policy_face_amount_USD_Denominated': 'Minimum Policy Face Amount (USD Denominated)',
        'Minimum_global_net_worth_USD_Denominated': 'Minimum Global Net Worth (USD Denominated)',
        'Age_related': 'Age Related',
        'Citizenship_visa_specified': 'Citizenship Visa Specified',
        'General': 'General',
        'Min_in_the_us_for_prior_12_months_annually_month': 'Min in US for Prior 12 Months (Annually)',
        'Min_in_the_us_for_prior_24_months_annually_month': 'Min in US for Prior 24 Months (Annually)',
        'Min_in_the_us_for_prior_48_months_annually_month': 'Min in US for Prior 48 Months (Annually)',
        'Min_in_the_us_annually_month': 'Min in US Annually',
        'Min_spend_outside_annually_month': 'Min Spend Outside Annually',
        'Physical_Citizenship': 'Physical Citizenship',
        'Visa': 'Visa',
        'Max_total_time_been_in_the_us_year': 'Max Total Time Been in US (Year)',
        'Financial_Citizenship': 'Financial Citizenship',
        'Residence': 'Residence',
        'Personal_insurance_flag': 'Personal Insurance Flag',
        'Need_for_US_based_coverage_flag': 'Need for US Based Coverage Flag',
        'Determining_justified_amounts': 'Determining Justified Amounts',
        'Bank_account_min_opened_time_prior_to_app_month': 'Bank Account Min Opened Time Prior to App (Month)',
        'Bank_account_info': 'Bank Account Info',
        'Bank_balance': 'Bank Balance',
        'Wealth': 'Wealth',
        'Time_of_verifiable_US_assets_in_the_US_month': 'Time of Verifiable US Assets in the US (Month)',
        'Verifiable_US_assets_in_the_US_million': 'Verifiable US Assets in the US (Million)',
        'Document_name': 'Document Name',
        'Document_notes': 'Document Notes',
        'Ownership_Structure': 'Ownership Structure',
        'Ownership_Structure_carrier_notes': 'Ownership Structure Carrier Notes',
        'Minimum_time_spend_outside_of_the_US_Per_Year_week': 'Minimum Time Spend Outside of the US (Per Year - Week)',
        'Foreign_country_specified': 'Foreign Country Specified',
        'Travel_Notes': 'Travel Notes',
        'Identities': 'Identities',
        'Acceptable_residing_country': 'Acceptable Residing Country',
        'Foreign_living_condition': 'Foreign Living Condition',
        'Exclusion': 'Exclusion',
        'Inbound_Identities': 'Inbound Identities',
        'Inbound_Citizenship': 'Inbound Citizenship',
        'Citizenship_exclusion_flag': 'Citizenship Exclusion Flag',
        'Acceptable_visa_status_type': 'Acceptable Visa Status Type',
        'Min_time_reside_in_us_per_year_month': 'Min Time Reside in US per Year (Month)',
        'Min_time_reside_in_us_month': 'Min Time Reside in US (Month)',
        'Continue_reside_flag': 'Continue Reside Flag',
        'Nexus_flag': 'Nexus Flag',
        'Max_foreign_travel_month': 'Max Foreign Travel (Month)',
        'Inbound_Policy_type': 'Inbound Policy Type',
        'Inbound_Notes': 'Inbound Notes'
    }

    # Get added features from FeatureRegistry and integrate into feature_dict
    additional_features = db.session.query(FeatureRegistry).all()
    for feature in additional_features:
        if feature.feature_name not in feature_dict:
            feature_dict[feature.feature_name] = feature.feature_name

    if request.method == 'POST':
        carrier_name = request.form.get('carrier_name')
        internal_code = request.form.get('internal_code')
        feature_name = request.form.get('feature_name')
        new_feature_name = request.form.get('new_feature_name')
        feature_value = request.form.get('feature_value')

        if feature_name == 'other':
            feature_name = new_feature_name

        if carrier_name and feature_name and feature_value:
            carrier_guid = str(uuid.uuid4())  # Generate new Carrier GUID
            new_carrier = Carrier(
                Carrier_GUID_PK=carrier_guid,
                Internal_code=internal_code,
                Insurance_company_name=carrier_name,
            )
            db.session.add(new_carrier)
            db.session.commit()


            new_feature = FeatureRegistry(
                carrier=new_carrier.Insurance_company_name,
                feature_name=feature_name,
                feature_value=feature_value
            )
            db.session.add(new_feature)
            db.session.commit()

            flash('Carrier added successfully!', category='success')
            return redirect(url_for('views.admin'))

    return render_template('add_carrier.html', carrier_values=carrier_values, feature_dict=feature_dict)
