# ============================================================
# SMARTSTOCK AI
# اختبار جلب Order مكتمل مباشرة من Square
# ============================================================

import sys
import os

# إضافة مجلد المشروع الرئيسي إلى مسار Python
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)

from integrations.square.square_client import SquareClient


# ============================================================
# إنشاء عميل Square
# ============================================================

square = SquareClient()


# ============================================================
# Order ID الذي تم دفعه وإتمامه سابقًا
# ============================================================

order_id = "pm1dMWlPowPWjTWBTQPT2kx227aZY"


# ============================================================
# جلب Order مباشرة
# ============================================================

order = square.get_order(order_id)


# ============================================================
# عرض النتيجة
# ============================================================

print("=" * 70)
print("SMARTSTOCK AI - ORDER DETAILS")
print("=" * 70)


if order:

    print("\nOrder Retrieved Successfully")

    print("\nOrder ID:")
    print(order.get("id"))

    print("\nLocation ID:")
    print(order.get("location_id"))

    print("\nState:")
    print(order.get("state"))

    print("\nCreated At:")
    print(order.get("created_at"))

    print("\nUpdated At:")
    print(order.get("updated_at"))

    print("\nTotal Money:")
    print(order.get("total_money"))

    print("\nLine Items:")

    for index, item in enumerate(
        order.get("line_items", []),
        start=1
    ):

        print(f"\n  Item #{index}")

        print("  Name:")
        print("  ", item.get("name"))

        print("  Quantity:")
        print("  ", item.get("quantity"))

        print("  Catalog Object ID:")
        print("  ", item.get("catalog_object_id"))

        print("  Total Money:")
        print("  ", item.get("total_money"))

else:

    print("\nFailed to retrieve Order.")


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)

