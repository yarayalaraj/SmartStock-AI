# ============================================================
# SMARTSTOCK AI
# اختبار قراءة المخزون من Square
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - SQUARE INVENTORY TEST")
print("=" * 60)

square = SquareClient()

# Variation ID الخاص بالمنتج
variation_id = "CHI74NB3HRW3WABQQJ2RUX42"

# Location ID الخاص بحساب Sandbox
location_id = "LCQJDMZ076NK1"

# جلب المخزون
counts = square.get_inventory_count(
    variation_id,
    location_id
)

print("=" * 60)

if counts is not None:

    print("INVENTORY API TEST: SUCCESS")

    if len(counts) == 0:

        print("لا توجد كمية مخزون مسجلة حاليًا.")

    else:

        for count in counts:

            print("-" * 40)
            print("Catalog Object ID:", count.get("catalog_object_id"))
            print("Location ID:", count.get("location_id"))
            print("State:", count.get("state"))
            print("Quantity:", count.get("quantity"))
            print("Calculated At:", count.get("calculated_at"))

else:

    print("INVENTORY API TEST: FAILED")

print("=" * 60)