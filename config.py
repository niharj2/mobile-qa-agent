import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# Android
ADB_PATH = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
OBSIDIAN_PACKAGE = "md.obsidian"

# Paths
SCREENSHOT_DIR = "screenshots"
LOG_DIR = "logs"

# Agent settings
MAX_STEPS = 12