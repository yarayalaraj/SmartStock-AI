# ============================================================
# SMARTSTOCK AI
# اختبار إتمام Order في Square Sandbox
# ============================================================

from integrations.square.square_client import SquareClient


print("=" * 60)
print("SMARTSTOCK AI - PAY ORDER TEST")
print("=" * 60)


# إنشاء عميل Square
square = SquareClient()


# Order ID الموجود لدينا
order_id = "pm1dMWlPowPWjTWBTQPT2kx227aZY"


# Payment ID الذي حصلنا عليه
payment_id = "V2CQnDnvjPezS8Eyf4Ra1S5vzQLZY"


# إتمام الطلب
order = square.pay_order(
    order_id,
    payment_id
)


print("=" * 60)


if order:

    print("PAY ORDER TEST: SUCCESS")

    print("-" * 40)

    print("Order ID:", order.get("id"))

    print("State:", order.get("state"))

    print("Total Money:", order.get("total_money"))

    print("Created At:", order.get("created_at"))

    line_items = order.get("line_items", [])

    print("Number of Items:", len(line_items))

else:

    print("PAY ORDER TEST: FAILED")


print("=" * 60)