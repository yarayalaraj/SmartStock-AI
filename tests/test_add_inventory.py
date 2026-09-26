# ============================================================
# SMARTSTOCK AI
# اختبار إضافة مخزون إلى Square
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - ADD INVENTORY TEST")
print("=" * 60)

square = SquareClient()

# Variation ID للمنتج
variation_id = "CHI74NB3HRW3WABQQJ2RUX42"

# Location ID
location_id = "LCQJDMZ076NK1"

# إضافة 10 وحدات إلى المخزون
result = square.add_inventory_stock(
    variation_id,
    location_id,
    10
)

print("=" * 60)

if result:

    print("ADD INVENTORY TEST: SUCCESS")

    # عرض الكمية التي أعادها Square
    counts = result.get("counts", [])

    for count in counts:

        print("-" * 40)
        print("Catalog Object ID:", count.get("catalog_object_id"))
        print("Location ID:", count.get("location_id"))
        print("State:", count.get("state"))
        print("Quantity:", count.get("quantity"))

else:

    print("ADD INVENTORY TEST: FAILED")

print("=" * 60)