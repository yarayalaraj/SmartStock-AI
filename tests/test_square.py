# ============================================================
# SMARTSTOCK AI
# اختبار الاتصال بـ Square API
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - SQUARE API TEST")
print("=" * 60)

# إنشاء عميل Square
square = SquareClient()

# اختبار الاتصال
result = square.test_connection()

print("=" * 60)

if result:
    print("SQUARE CONNECTION TEST: SUCCESS")
else:
    print("SQUARE CONNECTION TEST: FAILED")

print("=" * 60)