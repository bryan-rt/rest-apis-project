# app.py
import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from sqlalchemy import text
from dotenv import load_dotenv

from db import db
import models  # noqa: F401 - ensure models are imported so migrations see them
from resources.store import blp as StoreBlueprint
from resources.item import blp as ItemBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from blocklist import BLOCKLIST


def _build_db_uri(db_url_override=None):
    """
    Build a SQLAlchemy DB URI, refusing to fall back to SQLite in server environments.
    Also normalize postgres scheme for SQLAlchemy.
    """
    uri = db_url_override or os.getenv("DATABASE_URL")
    if not uri:
        # If you truly want SQLite for local dev, pass db_url="sqlite:///data.db"
        # to create_app() from your local runner instead of relying on a silent default.
        raise RuntimeError("DATABASE_URL is not set; refusing to fall back to SQLite.")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    # --- API / OpenAPI config ---
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # --- Database config (no silent SQLite fallback) ---
    app.config["SQLALCHEMY_DATABASE_URI"] = _build_db_uri(db_url)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)
    api = Api(app)

    # --- JWT config ---
    app.config["JWT_SECRET_KEY"] = "165809278171234852618889743169913726068"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

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

    # --- Register blueprints ---
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    # --- App-level debug routes (always on known paths) ---
    @app.get("/__debug/routes")
    def list_routes():
        return {"routes": sorted(str(r) for r in app.url_map.iter_rules())}, 200

    @app.get("/__debug/db")
    def db_debug():
        row = db.session.execute(
            text(
                """
                SELECT current_database() AS db,
                       current_user AS user_name,
                       inet_server_addr()::text AS host,
                       inet_server_port() AS port
                """
            )
        ).mappings().first()
        return dict(row), 200

    # Optional: log a masked DB URL once the engine is ready
    try:
        safe_url = str(db.engine.url)
        if db.engine.url.password:
            safe_url = safe_url.replace(db.engine.url.password, "***")
        app.logger.info(f"Connected DB URL: {safe_url}")
    except Exception:
        pass

    return app
