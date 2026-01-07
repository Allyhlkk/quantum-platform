from flask import Flask
from config import Config

from routes.main import main_bp
from routes.schmidt import schmidt_bp
from routes.chsh import chsh_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(main_bp)
    app.register_blueprint(schmidt_bp, url_prefix="/schmidt")
    app.register_blueprint(chsh_bp, url_prefix="/chsh")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
