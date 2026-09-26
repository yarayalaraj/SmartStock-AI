# ============================================================
# SMARTSTOCK AI
# اختبار إنشاء طلب في Square Sandbox
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - CREATE ORDER TEST")
print("=" * 60)


# إنشاء عميل Square
square = SquareClient()


# Location ID
location_id = "LCQJDMZ076NK1"


# Catalog Item Variation ID
variation_id = "CHI74NB3HRW3WABQQJ2RUX42"


# إنشاء طلب يحتوي على وحدة واحدة من المنتج
order = square.create_order(
    location_id,
    variation_id,
    1
)


print("=" * 60)


if order:

    print("CREATE ORDER TEST: SUCCESS")

    print("-" * 40)

    print("Order ID:", order.get("id"))

    print("Location ID:", order.get("location_id"))

    print("State:", order.get("state"))

    print("Created At:", order.get("created_at"))

    line_items = order.get("line_items", [])

    print("Number of Items:", len(line_items))

    for item in line_items:

        print("-" * 40)

        print("Catalog Object ID:",
              item.get("catalog_object_id"))

        print("Quantity:",
              item.get("quantity"))

else:

    print("CREATE ORDER TEST: FAILED")


print("=" * 60)