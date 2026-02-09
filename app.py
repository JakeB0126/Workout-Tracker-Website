import os

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager

from routes.auth import auth_bp
from routes.exercises import exercise_bp
from routes.users import user_bp


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET")
    if not app.config["JWT_SECRET_KEY"]:
        raise RuntimeError("JWT_SECRET is not set. Add it to .env.")

    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(exercise_bp)

    return app


# Backward compatibility for older local commands.
creat_app = create_app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
