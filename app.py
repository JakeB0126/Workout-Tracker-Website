import os
from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from routes.auth import auth_bp
from routes.users import user_bp

def creat_app() -> Flask:
    app = Flask(__name__)
    
    # Setup the Flask-JWT-Extended extension
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET")
    jwt = JWTManager(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    
    return app

if __name__ == "__main__":
    app = creat_app()
    app.run(debug=True)
    
