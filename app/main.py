from flask import Flask
from flask_cors import CORS

from app.config import settings
from app.routers.chat import chat_bp
from app.routers.reminders import reminders_bp
from app.routers.analytics import analytics_bp


def create_app():
    app = Flask(__name__)

    CORS(app, origins=[settings.NODE_BACKEND_URL])

    app.register_blueprint(chat_bp, url_prefix="/api/ai")
    app.register_blueprint(reminders_bp, url_prefix="/api/ai")
    app.register_blueprint(analytics_bp, url_prefix="/api/ai")

    @app.get("/")
    def root():
        return {"service": "HealthGuard AI Microservice", "status": "running", "version": "1.0.0"}

    @app.get("/health")
    def health():
        return {"status": "healthy", "ai_model": "gemini-2.0-flash"}

    return app


app = create_app()
