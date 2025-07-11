import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Set FOR4PAYMENTS_SECRET_KEY if not already set
if not os.environ.get("FOR4PAYMENTS_SECRET_KEY"):
    os.environ["FOR4PAYMENTS_SECRET_KEY"] = "a7903037-357c-46d6-a3cc-514d90f03342"

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    
    # Create all tables
    db.create_all()
    
    # Register routes
    from routes import register_routes
    register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)