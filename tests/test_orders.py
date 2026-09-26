# ============================================================
# SMARTSTOCK AI
# اختبار جلب المبيعات والطلبات من Square
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - SQUARE ORDERS TEST")
print("=" * 60)


# إنشاء عميل Square
square = SquareClient()


# Location ID الخاص بحساب Square
location_id = "LCQJDMZ076NK1"


# جلب الطلبات
orders = square.get_orders(
    location_id,
    limit=20
)


print("=" * 60)


if orders is not None:

    print("ORDERS API TEST: SUCCESS")

    print("-" * 40)

    print("Number of Orders:", len(orders))

    # عرض معلومات الطلبات الموجودة
    for order in orders:

        print("-" * 40)

        print("Order ID:", order.get("id"))

        print("Location ID:", order.get("location_id"))

        print("State:", order.get("state"))

        print("Created At:", order.get("created_at"))

        # عرض المنتجات داخل الطلب
        line_items = order.get("line_items", [])

        print("Number of Items:", len(line_items))

else:

    print("ORDERS API TEST: FAILED")


print("=" * 60)