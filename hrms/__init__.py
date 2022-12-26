from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = "5506b6b1de8c26ef3ee421e495f0e266"
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost:3306/qlnhansu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True

db = SQLAlchemy(app=app)

cloudinary.config(
    cloud_name='dg96ipqw3',
    api_key='347291246167297',
    api_secret='Nl2ti11GOwPGFHsOs8-5cXMDLJg'
)


login = LoginManager(app=app)