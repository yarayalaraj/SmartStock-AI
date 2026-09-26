# ============================================================
# SMARTSTOCK AI
# اختبار استرجاع Order محدد من Square
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - GET ORDER TEST")
print("=" * 60)


# إنشاء عميل Square
square = SquareClient()


# Order ID الذي أنشأناه سابقًا
order_id = "pm1dMWlPowPWjTWBTQPT2kx227aZY"


# استرجاع الطلب
order = square.get_order(order_id)


print("=" * 60)


if order:

    print("GET ORDER TEST: SUCCESS")

    print("-" * 40)

    print("Order ID:", order.get("id"))

    print("Location ID:", order.get("location_id"))

    print("State:", order.get("state"))

    print("Created At:", order.get("created_at"))

    print("Total Money:", order.get("total_money"))
    print("Total Money Net:", order.get("net_amounts", {}).get("total_money"))

    line_items = order.get("line_items", [])

    print("Number of Items:", len(line_items))

    for item in line_items:

        print("-" * 40)

        print(
            "Catalog Object ID:",
            item.get("catalog_object_id")
        )

        print(
            "Quantity:",
            item.get("quantity")
        )

else:

    print("GET ORDER TEST: FAILED")


print("=" * 60)