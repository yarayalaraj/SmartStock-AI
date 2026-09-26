# ============================================================
# SMARTSTOCK AI
# اختبار إنشاء منتج حقيقي داخل Square Sandbox
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - CREATE PRODUCT TEST")
print("=" * 60)

square = SquareClient()

# إنشاء منتج تجريبي داخل Square Sandbox
product = square.create_catalog_item(
    name="SmartStock Coffee",
    price=3.50
)

print("=" * 60)

if product:

    print("CREATE PRODUCT TEST: SUCCESS")

else:

    print("CREATE PRODUCT TEST: FAILED")

print("=" * 60)