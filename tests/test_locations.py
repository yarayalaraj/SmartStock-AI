# ============================================================
# SMARTSTOCK AI
# اختبار جلب مواقع Square
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - SQUARE LOCATIONS TEST")
print("=" * 60)

# إنشاء Square Client
square = SquareClient()

# جلب المواقع
locations = square.get_locations()

print("=" * 60)

if locations is not None:

    print("LOCATIONS API TEST: SUCCESS")
    print("عدد المواقع:", len(locations))

    # عرض بيانات المواقع
    for location in locations:

        print("-" * 40)
        print("Location ID:", location.get("id"))
        print("Name:", location.get("name"))
        print("Status:", location.get("status"))
        print("Country:", location.get("country"))
        print("Currency:", location.get("currency"))

else:

    print("LOCATIONS API TEST: FAILED")

print("=" * 60)