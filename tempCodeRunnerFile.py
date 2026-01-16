from flask import Flask
from config import Config

from routes.main import main_bp
from routes.analysis import analysis_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
