# ============================================================
# SMARTSTOCK AI
# Configuration
# ============================================================

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

# قراءة إعدادات Square
SQUARE_ACCESS_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN")

SQUARE_ENVIRONMENT = os.getenv(
    "SQUARE_ENVIRONMENT",
    "sandbox"
)

# تحديد رابط Square API
if SQUARE_ENVIRONMENT == "production":
    SQUARE_BASE_URL = "https://connect.squareup.com/v2"
else:
    SQUARE_BASE_URL = "https://connect.squareupsandbox.com/v2"


print("SmartStock configuration loaded.")
print("Square Environment:", SQUARE_ENVIRONMENT)
print("Square Base URL:", SQUARE_BASE_URL)