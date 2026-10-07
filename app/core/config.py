import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = os.getenv(
	"DATABASE_URL",
	f"sqlite:///{BASE_DIR / 'certificate_generator.db'}",
)
GENERATED_DIR = Path(os.getenv("GENERATED_DIR", str(BASE_DIR / "generated")))
APP_NAME = "Bulk Certificate Generator"
APP_VERSION = "1.0.0"