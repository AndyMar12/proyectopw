from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .routes import main_routes

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.config.from_pyfile('config.py', silent=True)  # Cargar configuración privada desde /instance/config.py
    
    # Inicializar la base de datos
    db.init_app(app)

    # Registrar las rutas
    app.register_blueprint(main_routes)

    return app