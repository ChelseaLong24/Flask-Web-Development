from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'kskidjd kdk'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://LAPTOP-MOJD6IUB\\SQLEXPRESS/ForeignNational?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .models import Carrier, Country, CountryResidenceMapping, CarrierInfo, USNexus, USNexusCarrierMapping, NRA, NRAPresenceTypeMapping, NRAFinancialPresence, NRAPhysicalPresence, SSN_TIN_document, Document_carrier_mapping, Approved_Ownership_Structure, Approved_Ownership_Structure_carrier_mapping, Foreign_Travel_Rules_for_USCitizens, Outbound_requirement, Inbound_requirement, ExPats_outbound_mapping, ExPats_Inbound_mapping

    app.register_blueprint(views, url_prefix = '/') #slash means no prefix
    app.register_blueprint(auth, url_prefix = '/')

    with app.app_context():
        db.create_all()  
    
    return app
