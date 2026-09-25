import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

# Absolute path resolution regardless of current working directory (CWD)
CORE_DIR = Path(__file__).resolve().parent
APP_DIR = CORE_DIR.parent
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent

# Ordered candidate locations for .env
CANDIDATE_ENV_PATHS = [
    BACKEND_DIR / ".env",
    ROOT_DIR / ".env",
    Path.cwd() / "backend" / ".env",
    Path.cwd() / ".env",
]


def load_environment() -> bool:
    """
    Search and load from candidate .env paths using absolute references.
    Returns True if an existing .env file was located and loaded.
    """
    loaded_any = False
    for env_path in CANDIDATE_ENV_PATHS:
        try:
            resolved = env_path.resolve()
            if resolved.is_file():
                load_dotenv(dotenv_path=resolved, override=True)
                loaded_any = True
        except OSError:
            continue
    return loaded_any


# Initial load on module import
load_environment()


class Settings(BaseModel):
    PROJECT_NAME: str = "Atles Backend"
    VERSION: str = "0.1.0"
    SERVICE_NAME: str = "Atles backend"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Provider & Model Settings
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    OLLAMA_TIMEOUT: float = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))
    ATLES_SYSTEM_PROMPT: str = os.getenv(
        "ATLES_SYSTEM_PROMPT",
        (
            "You are Atles, an intelligent, helpful, and concise personal AI assistant. "
            "Always identify as Atles and never refer to yourself as Qwen. "
            "Provide clear, accurate, and direct responses to assist the user."
        ),
    )

    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def OPENAI_API_KEY(self) -> str:
        """
        Dynamically retrieve OPENAI_API_KEY.
        If empty, re-attempts loading from candidate paths.
        """
        key = os.getenv("OPENAI_API_KEY", "")
        if not key or not key.strip():
            load_environment()
            key = os.getenv("OPENAI_API_KEY", "")
        return key.strip()

    @property
    def is_openai_configured(self) -> bool:
        return bool(self.OPENAI_API_KEY)


settings = Settings()
