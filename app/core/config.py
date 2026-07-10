import os

from dotenv import load_dotenv

# Load variables from a .env file (if present) into the environment.
load_dotenv()


class Settings:
    """
    Centralized application configuration, sourced from environment
    variables (with sensible local-development defaults).
    """

    APP_ENV: str = os.getenv("APP_ENV", "development")
    PORT: int = int(os.getenv("PORT", "8000"))

    # SQLite database file lives at the project root by default.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./task_tracker.db")


settings = Settings()