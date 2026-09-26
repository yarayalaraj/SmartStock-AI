# ============================================================
# SMARTSTOCK AI
# اختبار قراءة ملف .env
# ============================================================

from config.config import (
    SQUARE_ACCESS_TOKEN,
    SQUARE_ENVIRONMENT,
    SQUARE_BASE_URL
)

print("=" * 60)
print("SMARTSTOCK AI - CONFIGURATION TEST")
print("=" * 60)

print("Square Environment:", SQUARE_ENVIRONMENT)
print("Square Base URL:", SQUARE_BASE_URL)

if SQUARE_ACCESS_TOKEN:
    print("Square Access Token: FOUND")
else:
    print("Square Access Token: NOT SET")

print("=" * 60)
print("CONFIGURATION TEST COMPLETED")
print("=" * 60)