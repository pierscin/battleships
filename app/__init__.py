"""
Battleships application.
"""
from typing import Type

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config: Type[Config] = Config) -> Flask:
    """Creates app based on passed config."""
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    return app

from app import models
