from pathlib import Path

PATH_TO_EXCEL_FILE = Path(Path(__file__).parent.parent, "data", "operations.xlsx")
INVALID_PATH_TO_EXCEL_FILE = Path("operations.xlsx")
PATH_TO_USER_SETTINGS = Path(Path(__file__).parent, "user_settings.json")
PATH_TO_LOG_FILE = Path(Path(__file__).parent.parent, "logs", "utils.log")
PATH_TO_LOG_DIR = Path(Path(__file__).parent.parent, "logs")
