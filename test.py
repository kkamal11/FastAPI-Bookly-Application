from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_FOLDER = Path(BASE_DIR, "templates")
print(TEMPLATE_FOLDER)