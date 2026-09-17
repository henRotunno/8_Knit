import environ
from pathlib import Path

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

#Load .env from project root
environ.Env.read_env(BASE_DIR / ".env")