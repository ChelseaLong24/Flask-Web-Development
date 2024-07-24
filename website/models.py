from . import db

class Carrier(db.Model):
    __tablename__ = 'Carrier'
    
    Carrier_GUID_PK = db.Column(db.String(36), primary_key=True)
    Internal_code = db.Column(db.String(255), nullable=False)
    Insurance_company_name = db.Column(db.String(255), nullable=False)
    Alias_used_name = db.Column(db.String(255))
    Branch = db.Column(db.String(255))
    
    # Relationship to CountryResidenceMapping
    country_residence_mappings = db.relationship('CountryResidenceMapping', backref='carrier', lazy=True)


class Country(db.Model):
    __tablename__ = 'Country'
    
    Country_GUID_PK = db.Column(db.String(36), primary_key=True)
    Area = db.Column(db.String(255))
    Country = db.Column(db.String(255))
    City = db.Column(db.String(255))
    Region = db.Column(db.String(255))
    #Include_flag = db.Column(db.Boolean, default=False)
    Include_flag = db.Column(db.Integer, default=0)

    # Relationship to CountryResidenceMapping
    country_residence_mappings = db.relationship('CountryResidenceMapping', backref='country', lazy=True)

class CountryResidenceMapping(db.Model):
    __tablename__ = 'Country_residence_mapping'
    
    Country_residence_mapping_GUID_PK = db.Column(db.String(36), primary_key=True)
    Carrier_GUID_FK = db.Column(db.String(36), db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    Country_GUID_FK = db.Column(db.String(36), db.ForeignKey('Country.Country_GUID_PK'), nullable=False)
    Country_category = db.Column(db.String(255))
    Notes = db.Column(db.String(255))

class CarrierInfo(db.Model):
    __tablename__ = 'Carrier_info'
    
    Carrier_info_GUID_PK = db.Column(db.String(36), primary_key=True)
    Carrier_GUID_FK = db.Column(db.String(36), db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    Date_last_updated = db.Column(db.DateTime)
    Date_last_policy_inforce = db.Column(db.DateTime)
    Use_case_GUID_FK = db.Column(db.String(36), nullable=True)
    Financial_ratings_institution = db.Column(db.String(255), nullable=True)
    Ratings = db.Column(db.String(255), nullable=True)
    Notes = db.Column(db.Text, nullable=True)
    
    # Relationship to Carrier
    carrier = db.relationship('Carrier', backref=db.backref('carrier_infos', lazy=True))

class USNexus(db.Model):
    __tablename__ = 'US_Nexus'
    
    US_Nexus_GUID_PK = db.Column(db.String(36), primary_key=True)
    Nexus_Conditions = db.Column(db.Text, nullable=True)
    Nexus_Notes = db.Column(db.Text, nullable=True)

class USNexusCarrierMapping(db.Model):
    __tablename__ = 'US_Nexus_Carrier_mapping'
    
    US_Nexus_Carrier_mapping_GUID_PK = db.Column(db.String(36), primary_key=True)
    Carrier_GUID_FK = db.Column(db.String(36), db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    US_Nexus_GUID_FK = db.Column(db.String(36), db.ForeignKey('US_Nexus.US_Nexus_GUID_PK'), nullable=False)
    
    # Relationships
    carrier = db.relationship('Carrier', backref=db.backref('us_nexus_carrier_mappings', lazy=True))
    us_nexus = db.relationship('USNexus', backref=db.backref('us_nexus_carrier_mappings', lazy=True))

class NRA(db.Model):
    __tablename__ = 'NRA'
    
    NRA_GUID_PK = db.Column(db.String(36), primary_key=True)
    Carrier_GUID_FK = db.Column(db.String(36), db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    US_Nexus_flag = db.Column(db.Integer, default=0)
    Other_policy_related = db.Column(db.Text, nullable=True)
    Minimum_policy_face_amount_USD_Denominated = db.Column(db.Float, nullable=True)
    Minimum_global_net_worth_USD_Denominated = db.Column(db.Text, nullable=True)
    Age_related = db.Column(db.Text, nullable=True)
    Citizenship_visa_specified = db.Column(db.Text, nullable=True)
    Notes = db.Column(db.Text, nullable=True)

    # Relationships
    carrier = db.relationship('Carrier', backref=db.backref('nras', lazy=True))

class NRAPresenceTypeMapping(db.Model):
    __tablename__ = 'NRA_presence_type_mapping'
    
    NRA_presence_type_mapping_GUID_PK = db.Column(db.String(36), primary_key=True)
    NRA_GUID_FK = db.Column(db.String(36), db.ForeignKey('NRA.NRA_GUID_PK'), nullable=False)
    Physical_presence_GUID_FK = db.Column(db.String(36), db.ForeignKey('NRA_physical_presence.Physical_presence_GUID_PK'), nullable=False)
    Financial_presence_GUID_FK = db.Column(db.String(36), db.ForeignKey('NRA_financial_presence.Financial_presence_GUID_PK'), nullable=False)
    Notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    nra = db.relationship('NRA', backref=db.backref('nra_presence_type_mappings', lazy=True))
    physical_presence = db.relationship('NRAPhysicalPresence', backref=db.backref('nra_presence_type_mappings', lazy=True))
    financial_presence = db.relationship('NRAFinancialPresence', backref=db.backref('nra_presence_type_mappings', lazy=True))

class NRAFinancialPresence(db.Model):
    __tablename__ = 'NRA_financial_presence'
    
    Financial_presence_GUID_PK = db.Column(db.String(36), primary_key=True)
    Citizenship = db.Column(db.String(255), nullable=True)
    Residence = db.Column(db.String(255), nullable=True)
    Personal_insurance_flag = db.Column(db.Integer, default=0)
    Need_for_US_based_coverage_flag = db.Column(db.Integer, default=0)
    Determining_justified_amounts = db.Column(db.Text, nullable=True)
    Bank_account_min_opened_time_prior_to_app_month = db.Column(db.Float, nullable=True)
    Bank_account_info = db.Column(db.Text, nullable=True)
    Bank_balance = db.Column(db.Text, nullable=True)
    Wealth = db.Column(db.String(255), nullable=True)
    Time_of_verifiable_US_assets_in_the_US_month = db.Column(db.Text, nullable=True)
    Verifiable_US_assets_in_the_US_million = db.Column(db.Text, nullable=True)

class NRAPhysicalPresence(db.Model):
    __tablename__ = 'NRA_physical_presence'
    
    Physical_presence_GUID_PK = db.Column(db.String(36), primary_key=True)
    General = db.Column(db.Text, nullable=True)
    Min_in_the_us_for_prior_12_months_annually_month = db.Column(db.Float, nullable=True)
    Min_in_the_us_for_prior_24_months_annually_month = db.Column(db.Float, nullable=True)
    Min_in_the_us_for_prior_48_months_annually_month = db.Column(db.Float, nullable=True)
    Min_in_the_us_annually_month = db.Column(db.Float, nullable=True)
    Min_spend_outside_annually_month = db.Column(db.Float, nullable=True)
    Residence = db.Column(db.String(255), nullable=True)
    Citizenship = db.Column(db.String(255), nullable=True)
    Visa = db.Column(db.String(255), nullable=True)
    Max_total_time_been_in_the_us_year = db.Column(db.Float, nullable=True)

class SSN_TIN_document(db.Model):
    __tablename__ = 'SSN_TIN_document'

    Document_GUID_PK = db.Column(db.String, primary_key=True)
    Document_name = db.Column(db.String, nullable=False)

class Document_carrier_mapping(db.Model):
    __tablename__ = 'Document_carrier_mapping'

    Document_carrier_mapping_GUID_PK = db.Column(db.String, primary_key=True)
    Carrier_GUID_FK = db.Column(db.String, db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    Document_GUID_FK = db.Column(db.String, db.ForeignKey('SSN_TIN_document.Document_GUID_PK'), nullable=False)
    Document_notes = db.Column(db.String)

    carrier = db.relationship('Carrier', backref=db.backref('document_carrier_mappings', lazy=True))
    document = db.relationship('SSN_TIN_document', backref=db.backref('document_carrier_mappings', lazy=True))

class Approved_Ownership_Structure(db.Model):
    __tablename__ = 'Approved_Ownership_Structure'

    Approved_Ownership_Structure_GUID_PK = db.Column(db.String, primary_key=True)
    Ownership_Structure = db.Column(db.String, nullable=False)

class Approved_Ownership_Structure_carrier_mapping(db.Model):
    __tablename__ = 'Approved_Ownership_Structure_carrier_mapping'

    Approved_Ownership_Structure_carrier_mapping_GUID_PK = db.Column(db.String, primary_key=True)
    Carrier_GUID_FK = db.Column(db.String, db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    Approved_Ownership_Structure_GUID_FK = db.Column(db.String, db.ForeignKey('Approved_Ownership_Structure.Approved_Ownership_Structure_GUID_PK'), nullable=False)
    Ownership_Structure_carrier_notes = db.Column(db.String)

    carrier = db.relationship('Carrier', backref=db.backref('approved_ownership_structure_carrier_mappings', lazy=True))
    approved_ownership_structure = db.relationship('Approved_Ownership_Structure', backref=db.backref('approved_ownership_structure_carrier_mappings', lazy=True))

class Foreign_Travel_Rules_for_USCitizens(db.Model):
    __tablename__ = 'Foreign_Travel_Rules_for_USCitizens'

    Foreign_Travel_Rules_for_USCitizens_GUID_PK = db.Column(db.String, primary_key=True)
    Carrier_GUID_FK = db.Column(db.String, db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    Minimum_time_spend_outside_of_the_US_Per_Year_week = db.Column(db.String)
    Foreign_country_specified = db.Column(db.String)
    Notes = db.Column(db.String)

    carrier = db.relationship('Carrier', backref=db.backref('foreign_travel_rules', lazy=True))

class Outbound_requirement(db.Model):
    __tablename__ = 'Outbound_requirement'

    Outbound_requirement_GUID_PK = db.Column(db.String, primary_key=True)
    Outbound_requirement_detail = db.Column(db.String, nullable=False)

class Inbound_requirement(db.Model):
    __tablename__ = 'Inbound_requirement'

    Inbound_requirement_GUID_PK = db.Column(db.String, primary_key=True)
    Inbound_requirement_detail = db.Column(db.String, nullable=False)

class ExPats_outbound_mapping(db.Model):
    __tablename__ = 'ExPats_outbound_mapping'

    ExPats_Outbound_GUID_PK = db.Column(db.String, primary_key=True)
    Carrier_GUID_FK = db.Column(db.String, db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    Identities = db.Column(db.String, nullable=False)
    Acceptable_residing_country = db.Column(db.String, nullable=False)
    Outbound_requirement_GUID_FK = db.Column(db.String, db.ForeignKey('Outbound_requirement.Outbound_requirement_GUID_PK'), nullable=False)
    Policy_type = db.Column(db.String, nullable=False)
    Foreign_living_condition = db.Column(db.String, nullable=False)
    Exclusion = db.Column(db.String, nullable=False)

    carrier = db.relationship('Carrier', backref=db.backref('expats_outbound_mappings', lazy=True))
    outbound_requirement = db.relationship('Outbound_requirement', backref=db.backref('expats_outbound_mappings', lazy=True))

class ExPats_Inbound_mapping(db.Model):
    __tablename__ = 'ExPats_Inbound_mapping'

    ExPats_Inbound_GUID_PK = db.Column(db.String, primary_key=True)
    Carrier_GUID_FK = db.Column(db.String, db.ForeignKey('Carrier.Carrier_GUID_PK'), nullable=False)
    Inbound_requirement_GUID_FK = db.Column(db.String, db.ForeignKey('Inbound_requirement.Inbound_requirement_GUID_PK'), nullable=False)
    Identities = db.Column(db.String, nullable=False)
    Citizenship = db.Column(db.String, nullable=False)
    Citizenship_exclusion_flag = db.Column(db.Integer, default=0)
    Acceptable_visa_status_type = db.Column(db.String, nullable=False)
    Min_time_reside_in_us_per_year_month = db.Column(db.String, nullable=False)
    Min_time_reside_in_us_month = db.Column(db.String, nullable=False)
    Continue_reside_flag = db.Column(db.Integer, default=0)
    Nexus_flag = db.Column(db.Integer, default=0)
    Max_foreign_travel_month = db.Column(db.String, nullable=False)
    Policy_type = db.Column(db.String, nullable=False)
    Notes = db.Column(db.String, nullable=False)

    carrier = db.relationship('Carrier', backref=db.backref('expats_inbound_mappings', lazy=True))
    inbound_requirement = db.relationship('Inbound_requirement', backref=db.backref('expats_inbound_mappings', lazy=True))

class FeatureRegistry(db.Model):
    __tablename__ = 'feature_registry'
    id = db.Column(db.Integer, primary_key=True)
    carrier = db.Column(db.String(100), nullable=False)
    feature_name = db.Column(db.String(100), nullable=False)
    feature_value = db.Column(db.String(100), nullable=False)