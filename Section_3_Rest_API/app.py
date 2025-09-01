# app.py
import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from sqlalchemy import text
from dotenv import load_dotenv

from db import db
import models  # ensure models are imported so migrations see them
from resources.store import blp as StoreBlueprint
from resources.item import blp as ItemBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from blocklist import BLOCKLIST


def _resolve_db_uri(db_url_override=None):
    """Resolve a SQLAlchemy DB URI and normalize postgres scheme."""
    uri = db_url_override or os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URI")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    # Safe local fallback only if nothing provided (avoids crashes while developing)
    return uri or "sqlite:///data.db"


def create_app(db_url=None):
    load_dotenv()

    app = Flask(__name__)

    # --- API / OpenAPI config ---
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # --- Database ---
    app.config["SQLALCHEMY_DATABASE_URI"] = _resolve_db_uri(db_url)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    Migrate(app, db)

    # --- API / Blueprints ---
    api = Api(app)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    # --- JWT setup & handlers ---
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload.get("jti") in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has been revoked.", "error": "token_revoked"}), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token is not fresh.", "error": "fresh_token_required"}), 401

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        return {"is_admin": bool(identity == 1)}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"message": "Request does not contain an access token.", "error": "authorization_required"}), 401

    # --- App-level debug routes ---
    @app.get("/__debug/routes")
    def list_routes():
        return {"routes": sorted(str(r) for r in app.url_map.iter_rules())}, 200

    @app.get("/__debug/db")
    def db_debug():
        row = db.session.execute(text("""
            SELECT current_database() AS db,
                   current_user       AS user_name,
                   inet_server_addr()::text AS host,
                   inet_server_port() AS port
        """)).mappings().first()
        return dict(row), 200

    # Optional: log a masked DB URL at startup
    try:
        safe = str(db.engine.url)
        if db.engine.url.password:
            safe = safe.replace(db.engine.url.password, "***")
        app.logger.info(f"Connected DB URL: {safe}")
    except Exception:
        pass

    return app
